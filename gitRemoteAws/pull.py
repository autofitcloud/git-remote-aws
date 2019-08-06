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
from tqdm import tqdm

import logging
logger = logging.getLogger("git-remote-aws")

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
    MaxResults=3000 # FIXME <<<<<<<<<<<<<<<<<<<<<<<<<<<
    response_1 = ec2.describe_instances(
        DryRun=False, # False, # True, # |
        MaxResults=MaxResults # 1 # 30
    )
    # https://stackoverflow.com/a/55749807/4126114
    # , ec2.meta.region_name
    response_2 = postprocess_response(response_1)
    
    
    nr = 0 # counter to check if we're hitting the max above     
    for ri in tqdm(response_2, desc="Pulling instance desriptions"):
        nr+=1
        if nr==MaxResults: logger.warning("MaxResults=%i attained."%MaxResults)
        # save instance description
        fn_temp = os.path.join(fn['ec2DescInst'], ri['InstanceId']+'.json')
        # logger.debug("save ec2 desc to %s"%fn_temp)
        with open(fn_temp, 'w') as fh:
            json.dump(ri, fh, default=json_serial, indent=4, sort_keys=True)


# use jmespath like awscli
# https://stackoverflow.com/a/57018780/4126114
# Example
#   >>> mydata
#   {'foo': {'bar': [{'name': 'one'}, {'name': 'two'}]}}
#   >>> jmespath.search('foo.bar[?name==`one`]', mydata)
#   [{'name': 'one'}]
import jmespath

def get_cwCore(fn_dir, cloudwatch, operation_name, dict_key, **kwargs):
    """
    cloudwatch - boto3 cloudwatch client
    """
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Paginator.DescribeAlarms
    PaginationConfig = {
        'MaxResults': 3000 # FIXME <<<<<<<<<<<<<<<<<<<<<<<<<<<
    }

    # List alarms of insufficient data through the pagination interface
    # https://github.com/boto/boto3/blob/90c03b3aff081e13f5a8dfca2f37afe978ee4809/docs/source/guide/cw-example-creating-alarms.rst#describe-alarms
    # dimensions and namespace parameters
    # https://github.com/boto/boto3/blob/90c03b3aff081e13f5a8dfca2f37afe978ee4809/docs/source/guide/cw-example-metrics.rst#example
    # paginator = cloudwatch.get_paginator(operation_name, Namespace='AWS/EC2', MaxResults=MaxResults)
    paginator = cloudwatch.get_paginator(operation_name)
    for i, response in tqdm(enumerate(paginator.paginate(PaginationConfig=PaginationConfig, **kwargs)), desc="Downloading %s"%operation_name):
        # filter for instance descriptions
        #sys.stderr.write(json.dumps(list(response.keys()), default=json_serial, indent=4, sort_keys=True))
        #sys.stderr.write(json.dumps(response, default=json_serial, indent=4, sort_keys=True))
        #sys.stderr.write('\n')
        response[dict_key] = jmespath.search(dict_key+'[?Namespace==`AWS/EC2`]', response)
        
        for j, operation_i in enumerate(response[dict_key]):
            #sys.stderr.write("%s/%s: %s\n"%(i, j, json.dumps(operation_i['Dimensions'])))
            #return # FIXME
        
            # save instance description
            # Note that this is another filtering step that maybe is unnecessary
            # because any "AWS/EC2" namespace item should have the "InstanceId" dimension
            # Keeping it anyway because this code is untested ATM <<<<<<<<<<<<<<<<<<<<<<<<<<<<<< FIXME
            iid = [x['Value'] for x in operation_i['Dimensions'] if x['Name']=='InstanceId']
            if len(iid)==0: continue
            
            # sys.stderr.write(json.dumps(operation_i, default=json_serial, indent=4, sort_keys=True))
            # sys.stderr.write('\n')
    
            iid = iid[0]
            fn_temp = os.path.join(fn_dir, iid+'.json')
            #logger.debug("save ec2 desc to %s"%fn_temp)
            with open(fn_temp, 'w') as fh:
                json.dump(operation_i, fh, default=json_serial, indent=4, sort_keys=True)


def get_cwDescAlarms(fn_dir, cloudwatch):
    get_cwCore(fn_dir, cloudwatch, 'describe_alarms', 'MetricAlarms')


def get_cwListMetrics(fn_dir, cloudwatch):
    get_cwCore(fn_dir, cloudwatch, 'list_metrics', 'Metrics')
    
    
def get_sns_listTopics(fn_dir, sns):
    # SNS paginator
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#SNS.Paginator.ListTopics
    PaginationConfig = {
        'MaxResults': 3000 # FIXME <<<<<<<<<<<<<<<<<<<<<<<<<<<
    }
    operation_name = 'list_topics'
    dict_key = 'Topics'
    paginator = sns.get_paginator(operation_name)
    for i, response in tqdm(enumerate(paginator.paginate(PaginationConfig=PaginationConfig)), desc="Downloading SNS topics list"):
        for j, operation_i in enumerate(response[dict_key]):
            # sys.stderr.write("%s/%s: %s\n"%(i, j, json.dumps(operation_i)))
            #return # FIXME
        
            tid = operation_i['TopicArn'].split(':')[-1]
            fn_temp = os.path.join(fn_dir, tid+'.json')
            with open(fn_temp, 'w') as fh:
                json.dump(operation_i, fh, default=json_serial, indent=4, sort_keys=True)
    
    
import datetime as dt
def get_cwGetMetricData(fn_dir1, cloudwatch, ec2):
    """
    cloudwatch - boto3 client for cloudwatch service
    ec2 - boto3 resource for ec2 service
    """
    
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Paginator.GetMetricData
    stat_list=[
        'Maximum',
        'Average',
        'Minimum',
        'SampleCount'
    ]
    metric_list = [
        'CPUUtilization'
    ]
    # utility variable so that all recorded data at this point get marked with the same timestamp
    dt_now_d = dt.datetime.now()
    dt_now_s = str(dt_now_d)
    seconds_in_one_day = 60*60*24 # 86400  # used for granularity (daily)
    seconds_in_one_hour = 60*60
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Paginator.DescribeAlarms
    PaginationConfig = {
        'MaxResults': 3000 # FIXME <<<<<<<<<<<<<<<<<<<<<<<<<<<
    }

    # if permissions were ok, continue
    # check ec2 permissions
    # iterate over all regions

    # ec2.instances is of class ec2.instancesCollectionManager
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/collections.html
    for instance_obj in tqdm(ec2.instances.all(), desc="Downloading AWS Cloudwatch metrics"):
        # collect daily data as well as hourly data
        for n_days, period in [
            (90, seconds_in_one_day),
            (30, seconds_in_one_hour) # max n points is 1440, so cannot do 90 days with hourly in 1 shot
            ]:
        
            for stat_i in stat_list:
                for metric_i in metric_list:
                    
                    func_kwargs = dict(
                        MetricDataQueries = [
                            dict(
                                Id='m1', # ATM only 1 element in this list, so it doesn't matter
                                MetricStat=dict(
                                    Metric=dict(
                                        Namespace='AWS/EC2',
                                        MetricName=metric_i,
                                        Dimensions=[
                                            {
                                                'Name': 'InstanceId',
                                                'Value': instance_obj.id
                                            }
                                        ]
                                    ),
                                    Period=period,
                                    Stat=stat_i,
                                    Unit='Percent'
                                )
                            )
                        ],
                        StartTime=dt_now_d - dt.timedelta(days=n_days),
                        EndTime=dt_now_d
                    )
                    
                    # a description in simple english of the function arguments passed
                    desc_p1 = "%i seconds"%period
                    if period==seconds_in_one_day : desc_p1 = 'daily'
                    if period==seconds_in_one_hour: desc_p1 = 'hourly'
                    args_desc = '%s - %s - %i days - %s'%(metric_i, desc_p1, n_days, stat_i)

                    # path in which to save file
                    fn_dir2 = os.path.join(fn_dir1, args_desc)
                    os.makedirs(fn_dir2, exist_ok=True)
                    open(os.path.join(fn_dir2, '.gitkeep'), 'w').write('')
                    
                    # cannot use get_cwCore since the usage is different than describe-alarms and list-metrics                
                    operation_name='get_metric_data'
                    dict_key = 'MetricDataResults'
                    paginator = cloudwatch.get_paginator(operation_name)
                    for i, response in enumerate(paginator.paginate(PaginationConfig=PaginationConfig, **func_kwargs)):
                        for j, operation_i in enumerate(response[dict_key]):
                            fn_temp = os.path.join(fn_dir2, instance_obj.id+'.json')
                            with open(fn_temp, 'w') as fh:
                                json.dump(operation_i, fh, default=json_serial, indent=4, sort_keys=True)
              
              
"""
Just moving this out of ec2op for later integration
Check https://gitlab.com/autofitcloud/git-remote-aws/issues/4

def cw_getMetricStatistics(instance_id, cloudwatch):

    # utility variable so that all recorded data at this point get marked with the same timestamp
    dt_now_d = dt.datetime.now()
    dt_now_s = str(dt_now_d)
    seconds_in_one_day = 60*60*24 # 86400  # used for granularity (daily)
    seconds_in_one_hour = 60*60

    # if permissions were ok, continue
    # check ec2 permissions
    # iterate over all regions

    # collect daily data as well as hourly data
    for n_days, period in [
        (90, seconds_in_one_day),
        (30, seconds_in_one_hour) # max n points is 1440, so cannot do 90 days with hourly in 1 shot
        ]:
        func_args_1 = dict(
            Namespace='AWS/EC2',
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': instance_id
                }
            ],
            MetricName='CPUUtilization',
            StartTime=dt_now_d - dt.timedelta(days=n_days),
            EndTime=dt_now_d,
            Period=period,
            Statistics=[
                'Maximum',
                'Average',
                'Minimum',
                'SampleCount'
            ],
            Unit='Percent'
        )
        desc_p1 = "(every %s seconds)"%period
        if period==seconds_in_one_day : desc_p1 = 'daily'
        if period==seconds_in_one_hour: desc_p1 = 'hourly'
        args_desc = 'CPU %s for %i days'%(desc_p1, n_days) # a description in simple english of the function arguments passed
        #print("processing", args_desc)

        response_1 = cloudwatch.get_metric_statistics(**func_args_1)

        response_2 = {
            'InstanceId': instance_id,
            'ArgsDesc': args_desc,
            'FetchTimestamp': dt_now_s,
            'CloudwatchMetricArgs': func_args_1,
            'CloudwatchMetricStatistics': response_1
        }

        yield response_2, args_desc
"""
                
                
EC2INSTANCESINFO = 'http://www.ec2instances.info/instances.json'
def get_awsCat(fn, ec2catalog=None):
    ec2catalog = EC2INSTANCESINFO
    logger.info("getting aws catalog from %s"%ec2catalog)

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
    fn['awsCat'] = os.path.join(fn['root'], 'www.ec2instances.info')
    #logger.debug("mkdir %s"%fn['awsCat'])
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



