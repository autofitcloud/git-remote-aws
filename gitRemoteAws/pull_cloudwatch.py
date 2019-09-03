from .utils import json_serial
from tqdm import tqdm
import os
import json



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
            
            # hourly data
            # max n points is 1440, so cannot do 90 days with hourly in 1 shot
            # FIXME comment out since not used yet
            # (30, seconds_in_one_hour)
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
