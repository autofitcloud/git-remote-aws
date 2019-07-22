# RuntimeError: Click will abort further execution because Python 3 was configured to use ASCII as encoding for the environment. 
# Consult https://click.palletsprojects.com/en/7.x/python3/ for mitigation steps.
import os
os.environ["LC_ALL"] = "C.UTF-8"
os.environ["LANG"]   = "C.UTF-8"


from urllib.parse import urlparse
import json
import sys
import click
import boto3
import logging

from .cli_ec2 import Ec2Class, cli_core
from .pull import SessionMan, get_cwDescAlarms, get_cwListMetrics, get_cwGetMetricData
from .dotman import DotMan
import copy

logger = logging.getLogger('git-remote-aws')

class CwClass(Ec2Class):

  def list(self):
    logger.debug('ec2class.list')
    profile_name = self.remote_parsed.username or 'default'
    
    # Debugging to file since stdout from this script does not go to terminal after git pull
    # Only the exit code survives.
    # with open('file.txt', 'w') as fp:
    #   fp.write(self.remote_parsed.hostname)
    #   fp.write("\n")
    #   fp.write(self.remote_parsed.path)
    #   fp.write("\n")

    logger.debug("parsed scheme, hostname, path")
    logger.debug(self.remote_parsed.scheme)
    logger.debug(self.remote_parsed.hostname)
    logger.debug(self.remote_parsed.path)
    
    self.makedirsRegion()
    
    if self.remote_parsed.path == '/list-metrics':
      return self.get_cw_listMetrics()
      
    if self.remote_parsed.path=='/describe-alarms':
      return self.get_cw_descAlarms()

    if self.remote_parsed.path=='/get-metric-data':
      return self.get_cw_getMetricData()
      
    logger.warning("remote url not supported. Skipping: %s"%self.remote_url)
    
  def get_cw_descAlarms(self):
    fn = copy.deepcopy(self.dm.fn)

    # prep inst desc
    fn['cwDescAlarms'] = self.dm.cwDescAlarms(self.my_region)
    #logger.debug("mkdir %s"%fn['ec2DescInst'])
    os.makedirs(fn['cwDescAlarms'], exist_ok=True)

    # get instance descriptions
    logger.debug('Cloning AWS CW describe-alarms')
    cloudwatch = self.session.client('cloudwatch')
    get_cwDescAlarms(fn['cwDescAlarms'], cloudwatch)

  def get_cw_listMetrics(self):
    fn = copy.deepcopy(self.dm.fn)

    # prep inst desc
    fn['cwListMetrics'] = self.dm.cwListMetrics(self.my_region)
    #logger.debug("mkdir %s"%fn['ec2DescInst'])
    os.makedirs(fn['cwListMetrics'], exist_ok=True)

    # get instance descriptions
    logger.debug('Cloning AWS CW list-metrics')
    cloudwatch = self.session.client('cloudwatch')
    get_cwListMetrics(fn['cwListMetrics'], cloudwatch)

  def get_cw_getMetricData(self):
    fn = copy.deepcopy(self.dm.fn)

    # prep inst desc
    fn['cwGetMetricData'] = self.dm.cwGetMetricData(self.my_region)
    #logger.debug("mkdir %s"%fn['ec2DescInst'])
    os.makedirs(fn['cwGetMetricData'], exist_ok=True)

    # get instance descriptions
    logger.debug('Cloning AWS CW get-metric-data')
    cloudwatch = self.session.client('cloudwatch')
    ec2 = self.session.getSession().resource('ec2')
    get_cwGetMetricData(fn['cwGetMetricData'], cloudwatch, ec2)

  def capabilities(self):
    sys.stdout.write("import\n")
    
    # add refspec capability
    # treats error but I don't implement this properly
    # Copied from 
    # https://github.com/glandium/git-cinnabar/blob/9aec8ed11752ca35fe9e5581cda2b7f16aa86d0d/cinnabar/remote_helper.py#L112
    sys.stdout.write("refspec HEAD:refs/aws+cw/HEAD\n")



#-----------------

@click.command()
@click.argument('remote_name')
@click.argument('remote_url')
def cli(remote_name, remote_url):
    cli_core(remote_name, remote_url, CwClass)


if __name__ == '__main__':
  cli()