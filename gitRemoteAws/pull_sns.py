from tqdm import tqdm
import os
import json
from .utils import json_serial


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
