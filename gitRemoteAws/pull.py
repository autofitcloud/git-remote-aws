# Copied from gitlab.com/shadiakiki1986/ec2optimizer
# and modified as needed

from botocore.exceptions import ClientError
from .botoman import SessionMan
import importlib
import yaml
import os
import sys
import datetime as dt
import json
import requests
from cachecontrol import CacheControl
import pandas as pd
import copy

##############################
# from lambda_login.py and lambda_ec2_describeInstances.py

def postprocess_response(response_1):
    if 'Reservations' not in response_1:
        return
    
    for res_i, res_v in enumerate(response_1['Reservations']):
        for i_desc in res_v['Instances']:

            # put dict to ddb
            item = {
                # keys
                'InstanceId': i_desc['InstanceId'],

                # some fields duplicated out of the original response
        		'OwnerId': response_1['Reservations'][res_i]['OwnerId'], # eg '886436197218'
        		'ReservationId': response_1['Reservations'][res_i]['ReservationId'], # eg 'r-e5813ce8'

                # core info
                'InstanceDescription': i_desc
            }
            yield item


def json_serial(obj):
    """
    JSON serializer for objects not serializable by default json code
    http://stackoverflow.com/questions/11875770/ddg#22238613
    """
    if isinstance(obj, (dt.datetime, dt.date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))


def get_instDesc(fn, ec2):
    """
    ec2 - boto3 ec2 client
    """
    MaxResults=30 # FIXME <<<<<<<<<<<<<<<<<<<<<<<<<<<
    response_1 = ec2.describe_instances(
        DryRun=False, # False, # True, # |
        MaxResults=MaxResults # 1 # 30
    )
    # https://stackoverflow.com/a/55749807/4126114
    # , ec2.meta.region_name
    response_2 = postprocess_response(response_1)

    for ri in response_2:
        # save instance description
        fn_temp = os.path.join(fn['ec2DescInst'], ri['InstanceId']+'.json')
        # print("save ec2 desc to %s"%fn_temp)
        with open(fn_temp, 'w') as fh:
            json.dump(ri, fh, default=json_serial, indent=4, sort_keys=True)



def get_cwDescAlarms(fn, cloudwatch):
    """
    cloudwatch - boto3 cloudwatch client
    """
    MaxResults=30 # FIXME <<<<<<<<<<<<<<<<<<<<<<<<<<<
    MaxPages = 5

    # List alarms of insufficient data through the pagination interface
    # https://github.com/boto/boto3/blob/90c03b3aff081e13f5a8dfca2f37afe978ee4809/docs/source/guide/cw-example-creating-alarms.rst#describe-alarms
    # dimensions and namespace parameters
    # https://github.com/boto/boto3/blob/90c03b3aff081e13f5a8dfca2f37afe978ee4809/docs/source/guide/cw-example-metrics.rst#example
    paginator = cloudwatch.get_paginator('describe_alarms', Namespace='AWS/EC2', MaxResults=MaxResults)
    for i, response in enumerate(paginator.paginate()):
        if i > MaxPages: break

        # save instance description
        iid = [x['Value'] for x in response['Dimensions'] if x['Name']=='InstanceId'][0]
        fn_temp = os.path.join(fn['cwDescAlarms'], iid+'.json')
        #print("save ec2 desc to %s"%fn_temp)
        with open(fn_temp, 'w') as fh:
            json.dump(ri, fh, default=json_serial, indent=4, sort_keys=True)



EC2INSTANCESINFO = 'http://www.ec2instances.info/instances.json'
def get_awsCat(fn, ec2catalog=None):
    ec2catalog = EC2INSTANCESINFO
    print("getting aws catalog from %s"%ec2catalog)

    # non-cached
    # https://3.python-requests.org/
    # from requests import HTTPSession
    # http = HTTPSession()
    # r = http.request('get', ec2catalog)

    # cached https://cachecontrol.readthedocs.io/en/latest/
    sess = requests.session()
    cached_sess = CacheControl(sess)
    r = cached_sess.request('get', ec2catalog)

    df_json = json.dumps(r.json(), indent=4, sort_keys=True)

    # prep save
    fn['awsCat'] = os.path.join(fn['dot'], 'www.ec2instances.info')
    #print("mkdir %s"%fn['awsCat'])
    os.makedirs(fn['awsCat'], exist_ok=True)

    # save raw
    fn_temp = os.path.join(fn['awsCat'], 't0_raw.json')
    with open(fn_temp, 'w') as fh:
        fh.write(df_json)

    # postprocess (from colab/20190624-crow/t1-raw aws)
    # df = pd.read_json(r.json())
    df = pd.DataFrame(r.json()) # [:2]

    # process for back-compatibility
    default_priceRegion = df['pricing'].keys()[0]
    if 'linux' in df['pricing'][default_priceRegion]:
        df['pricing'] = df['pricing'][default_priceRegion]['linux']['ondemand']
    else:
        df['pricing'] = None

    df = df.rename(columns={
        'instance_type': 'API Name',
        'vCPU': 'vCPUs',
        'memory': 'Memory',
        'storage': 'Instance Storage',
        'network_performance': 'Network Performance',
        'pricing': 'Linux On Demand cost',
    })

    # proceed
    df = df[['API Name', 'vCPUs', 'Memory', 'Instance Storage', 'Network Performance', 'Linux On Demand cost']]

    df['family_l1'] = df['API Name'].str.split('.').apply(lambda x: x[0][0])
    df['family_l2'] = df['API Name'].str.split('.').apply(lambda x: x[0])
    #df['vCPUs'] = df['vCPUs'].str.split(' ').apply(lambda x: x[0]).astype(int)
    #df['Memory'] = df['Memory'].str.split(' ').apply(lambda x: x[0]).astype(float)
    #df['Linux On Demand cost'] = ( df['Linux On Demand cost']
    #                                   .str.replace('unavailable', '')
    #                                   .str.split(' ')
    #                                   .apply(lambda x: x[0])
    #                                   .str.replace('$','')
    #                                   .map(lambda x: None if x=='' else float(x))
    #                             )

    df = df.sort_values(['family_l1', 'family_l2', 'vCPUs', 'Memory'])
    # df.set_index(['family_l1', 'family_l2', 'API Name'], inplace=True)
    #df = df.sort_index()

    # df_json = df.reset_index().to_json(orient='split')
    df_json = df.to_json(orient='split')

    # pretty-print
    df_json = json.dumps(json.loads(df_json), indent=4, sort_keys=True)

    # save
    fn_temp = os.path.join(fn['awsCat'], 't1_processed.json')
    with open(fn_temp, 'w') as fh:
        fh.write(df_json)

    # append smaller types - family_l1
    df_l1 = df.copy()
    df_l1 = df_l1.sort_values(['family_l1', 'vCPUs', 'Memory', 'family_l2']) # notice the sorting fields
    df_l1['type_smaller'] = df_l1.groupby('family_l1')['API Name'].shift(+1)
    df_l1 = df_l1.merge(
        df_l1[['API Name', 'vCPUs', 'Memory', 'Linux On Demand cost']].rename(columns={'API Name': 'type_smaller'}),
        on='type_smaller',
        how='outer',
        suffixes=['', '_smaller']
    )
    df_l1 = df_l1.sort_values(['family_l1', 'family_l2', 'vCPUs', 'Memory'])
    df_l1.set_index(['family_l1','family_l2','API Name'], inplace=True)

    df_l1['ratio_cpu'] = df_l1.vCPUs / df_l1.vCPUs_smaller
    df_l1['ratio_mem'] = df_l1.Memory / df_l1.Memory_smaller
    # df_l1['ratio_min'] = df_l1[['ratio_cpu', 'ratio_mem']].min(axis=1)
    df_l1['ratio_max'] = df_l1[['ratio_cpu', 'ratio_mem']].max(axis=1) # this is the bottleneck
    dfl1_json = df_l1.reset_index().to_json(orient='split')
    dfl1_json = json.dumps(json.loads(dfl1_json), indent=4, sort_keys=True) # pretty-print

    # save
    fn_temp = os.path.join(fn['awsCat'], 't3a_smaller_familyL1.json')
    with open(fn_temp, 'w') as fh:
        fh.write(dfl1_json)

    # append smaller types - family_l2
    df_l2 = df.reset_index().copy()
    df_l2 = df_l2.sort_values(['family_l1', 'family_l2', 'vCPUs', 'Memory']) # notice the sorting fields
    df_l2['type_smaller'] = df_l2.groupby('family_l2')['API Name'].shift(+1) # notice the groupby field
    df_l2 = df_l2.merge(
        df_l2[['API Name', 'vCPUs', 'Memory', 'Linux On Demand cost']].rename(columns={'API Name': 'type_smaller'}),
        on='type_smaller',
        how='outer',
        suffixes=['', '_smaller']
    )
    df_l2 = df_l2.sort_values(['family_l1', 'family_l2', 'vCPUs', 'Memory'])
    df_l2.set_index(['family_l1','family_l2','API Name'], inplace=True)

    df_l2['ratio_cpu'] = df_l2.vCPUs / df_l2.vCPUs_smaller
    df_l2['ratio_mem'] = df_l2.Memory / df_l2.Memory_smaller
    # df_l2['ratio_min'] = df_l2[['ratio_cpu', 'ratio_mem']].min(axis=1)
    df_l2['ratio_max'] = df_l2[['ratio_cpu', 'ratio_mem']].max(axis=1) # this is the bottleneck
    dfl2_json = df_l2.reset_index().to_json(orient='split')
    dfl2_json = json.dumps(json.loads(dfl2_json), indent=4, sort_keys=True) # pretty-print

    # save
    fn_temp = os.path.join(fn['awsCat'], 't3b_smaller_familyL2.json')
    with open(fn_temp, 'w') as fh:
        fh.write(dfl2_json)





def main(dm, repository_name, repository_url):
    """
    dm - instance of DotMan
    repository_name - name of remote repo
    repository_url - url of remote repo
    """
    fn = copy.deepcopy(dm.fn)

    # get region https://stackoverflow.com/a/37519906/4126114
    session = SessionMan(dm)
    my_region = session.getSession().region_name
    #region_name is basically defined as session.get_config_variable('region')
    # print("sts region", my_region)

    if my_region is None:
        print("fatal: failed to detect region name.")
        print("Are you sure you configured awscli? Check files in %s"%dm.fn['aws_dot'])
        sys.exit(1)

    fn['pull_region_one'] = dm.pull_region_one(my_region)
    #print("mkdir %s"%fn['pull_region_one'])
    os.makedirs(fn['pull_region_one'], exist_ok=True)

    if repository_url=='aws://ec2.aws.amazon.com/describe-instances':
        # prep inst desc
        fn['ec2DescInst'] = dm.ec2DescInst(my_region)
        #print("mkdir %s"%fn['ec2DescInst'])
        os.makedirs(fn['ec2DescInst'], exist_ok=True)

        # get instance descriptions
        print('Cloning AWS EC2 description data')
        ec2 = session.client('ec2')
        get_instDesc(fn, ec2)

        return

    if repository_url==EC2INSTANCESINFO:
        # get aws catalog
        print('Cloning AWS EC2 catalog')
        get_awsCat(fn)

        return

    if repository_url=='aws://cloudwatch.describe-alarms':
        # prep inst desc
        fn['cwDescAlarms'] = dm.cwDescAlarms(my_region)
        #print("mkdir %s"%fn['ec2DescInst'])
        os.makedirs(fn['cwDescAlarms'], exist_ok=True)

        # get instance descriptions
        print('Cloning AWS CW describe-alarms')
        cloudwatch = session.client('cloudwatch')
        get_cwDescAlarms(fn, ec2)

        return


    # unknown pull action for remote
    print("warning: Unknown how to pull from %s, %s . Skipping"%(repository_name, repository_url))
    return
