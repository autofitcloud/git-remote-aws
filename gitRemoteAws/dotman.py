# Copied from gitlab.com/shadiakiki1986/ec2optimizer
# and modified as needed

"""
Manager of ec2op dot folder and file structure
"""
import sys
import yaml
import os
from collections import OrderedDict

class DotMan:

    def __init__(self, rootdir='.'):
        self.rootdir = rootdir
        self.fn = self.maindirs()

    def maindirs(self):
        # define important paths
        fn=OrderedDict()
        fn['root'] = os.path.abspath(self.rootdir)
        fn['repo_aws'] = os.path.join(fn['root'], 'aws.amazon.com')
        fn['pull_region_root'] = os.path.join(fn['repo_aws'])
        fn['optimize_region_root'] = os.path.join(fn['root'], 'regions')
        fn['aws_dot'] = os.path.expanduser("~/.aws")
        fn['aws_credentials'] = os.path.join(fn['aws_dot'], 'credentials')
        fn['awsCat'] = os.path.join(fn['root'], 'www.ec2instances.info')
        return fn

    def pull_region_one(self, region):
        return os.path.join(self.fn['pull_region_root'], region)

    def optimize_region_one(self, region):
        return os.path.join(self.fn['optimize_region_root'], region)

    def regRecAdded(self, region):
        return os.path.join(self.pull_region_one(region), 'recommendations', 'added')

    def regRecPend(self, region):
        return os.path.join(self.optimize_region_one(region), 'recommendations', 'pending')

    def regRecCommittedPend(self, region):
        return os.path.join(self.optimize_region_one(region), 'recommendations', 'committed', 'pending')

    def regRecCommittedPushed(self, region):
        return os.path.join(self.optimize_region_one(region), 'recommendations', 'committed', 'pushed')

    def ec2DescInst(self, region):
        return os.path.join(self.pull_region_one(region), 'ec2_describeInstances')

    def cwDescAlarms(self, region):
        return os.path.join(self.pull_region_one(region), 'cw_describeAlarms')

    def cwListMetrics(self, region):
        return os.path.join(self.pull_region_one(region), 'cw_listMetrics')

    def cwGetMetricData(self, region):
        return os.path.join(self.pull_region_one(region), 'cw_getMetricData')
        
    def snsListTopics(self, region):
        return os.path.join(self.pull_region_one(region), 'snsListTopics')