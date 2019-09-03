# Copied from gitlab.com/shadiakiki1986/ec2optimizer
# and modified as needed

from botocore.exceptions import ClientError
# from .botoman import SessionMan
import importlib
import yaml
import os
import sys
import datetime as dt
import json
import requests
from cachecontrol import CacheControl
import pandas as pd
import numpy as np
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


from .utils import json_serial

def get_instDesc(fn, ec2, fulldata):
    """
    fn - dict of local file paths to use
    ec2 - boto3 ec2 client
    fulldata - boolean, True when all data is to be dumped into the output. False when only the minimal necessary data is needed.
    """
    MaxResults=3000 # FIXME <<<<<<<<<<<<<<<<<<<<<<<<<<<
    
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances
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
        
        # trim information if not "fulldata"
        if not fulldata:
            ri.pop('OwnerId', None)
            ri.pop('ReservationId', None)
            ri['InstanceDescription'] = { k: ri['InstanceDescription'][k]
                                          for k in ri['InstanceDescription'].keys()
                                          if k in ['CpuOptions', 'InstanceType', 'InstanceId', 'Tags', 'State']
                                        }

        # save instance description
        fn_temp = os.path.join(fn['ec2DescInst'], ri['InstanceId']+'.json')
        # logger.debug("save ec2 desc to %s"%fn_temp)
        with open(fn_temp, 'w') as fh:
            json.dump(ri, fh, default=json_serial, indent=4, sort_keys=True)



    
    

                
                
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
    #logger.debug("mkdir %s"%fn['awsCat'])
    os.makedirs(fn['awsCat'], exist_ok=True)

    # save raw
    fn_temp = os.path.join(fn['awsCat'], 't0_raw.json')
    with open(fn_temp, 'w') as fh:
        fh.write(df_json)
        

    # Convert json to pandas dataframe
    # Test live with
    # >>> import pandas as pd, json
    # >>> df = pd.DataFrame(json.load(open("core/www.ec2instances.info/t0_raw.json")))
    # >>> df.head()
    #
    # df_pd = pd.read_json(r.json())
    df_pd = pd.DataFrame(r.json()) # [:2]

    # Gather prices from different regions into a list and calculate the average
    # remember that default_priceRegion goes to the pandas dataframe index, and the output is a dict, so all keys after that go to the python dict
    df_pd['price_list'] = df_pd['pricing'].apply(lambda x: np.array([float(x[y]['linux']['ondemand']) for y in x.keys() if 'linux' in x[y]]))
    df_pd['price_avg'] = df_pd['price_list'].apply(lambda x: None if len(x)==0 else np.average(x))
    
    # check that the prices in all the regions do not differ by more than 20%
    # In fact, there are plenty of price differences > 20%
    # eg 'c5d.xlarge' min/max are 0.192/0.252
    # So won't check this anymore
    # df_pd['price_min'] = df_pd['price_list'].apply(lambda x: None if len(x)==0 else x.min())
    # df_pd['price_max'] = df_pd['price_list'].apply(lambda x: None if len(x)==0 else x.max())
    # df_pd['price_diff'] = (df_pd['price_max'] - df_pd['price_min'])/df_pd['price_min']*100
    #if (df_pd['price_diff'] > 20).any():
    #    logger.warning("Found instance types with price difference within regions > 20%%: %s. Aborting"%(', '.join(df_pd.instance_type[df_pd['price_diff'] > 20].values)))

    # logger.debug("df_pd.head")
    # logger.debug(df_pd[['price_min', 'price_avg', 'price_max']].head())
    
    # replace the "pricing" field from a nested dict with the average
    # (from colab/20190624-crow/t1-raw aws)
    # This is for back-compatibility since my code expects pricing to be a single float
    df_pd['pricing'] = df_pd['price_avg']

    # rename columns as needed
    df_pd = df_pd.rename(columns={
        'instance_type': 'API Name',
        'vCPU': 'vCPUs',
        'memory': 'Memory',
        'storage': 'Instance Storage',
        'network_performance': 'Network Performance',
        'pricing': 'Linux On Demand cost',
    })

    # proceed
    df_pd = df_pd[['API Name', 'vCPUs', 'Memory', 'Instance Storage', 'Network Performance', 'Linux On Demand cost']]

    df_pd['family_l1'] = df_pd['API Name'].str.split('.').apply(lambda x: x[0][0])
    df_pd['family_l2'] = df_pd['API Name'].str.split('.').apply(lambda x: x[0])
    #df_pd['vCPUs'] = df_pd['vCPUs'].str.split(' ').apply(lambda x: x[0]).astype(int)
    #df_pd['Memory'] = df_pd['Memory'].str.split(' ').apply(lambda x: x[0]).astype(float)
    #df_pd['Linux On Demand cost'] = ( df_pd['Linux On Demand cost']
    #                                   .str.replace('unavailable', '')
    #                                   .str.split(' ')
    #                                   .apply(lambda x: x[0])
    #                                   .str.replace('$','')
    #                                   .map(lambda x: None if x=='' else float(x))
    #                             )

    df_pd = df_pd.sort_values(['family_l1', 'family_l2', 'vCPUs', 'Memory'])
    # df_pd.set_index(['family_l1', 'family_l2', 'API Name'], inplace=True)
    #df_pd = df_pd.sort_index()

    # df_json = df_pd.reset_index().to_json(orient='split')
    df_json = df_pd.to_json(orient='split')

    # pretty-print
    df_json = json.dumps(json.loads(df_json), indent=4, sort_keys=True)

    # save
    fn_temp = os.path.join(fn['awsCat'], 't1_processed.json')
    with open(fn_temp, 'w') as fh:
        fh.write(df_json)

    # append smaller types - family_l1
    df_l1 = df_pd.copy()
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
    df_l2 = df_pd.reset_index().copy()
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



