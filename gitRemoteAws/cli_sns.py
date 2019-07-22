# RuntimeError: Click will abort further execution because Python 3 was configured to use ASCII as encoding for the environment. 
# Consult https://click.palletsprojects.com/en/7.x/python3/ for mitigation steps.
import os
os.environ["LC_ALL"] = "C.UTF-8"
os.environ["LANG"]   = "C.UTF-8"

# SNS CLI
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#SNS.Paginator.ListTopics

from urllib.parse import urlparse
import json
import sys
import click
import boto3
import logging

from .cli_ec2 import Ec2Class, cli_core
from .pull import get_sns_listTopics
from .dotman import DotMan
import copy

logger = logging.getLogger('git-remote-aws')

class SnsClass(Ec2Class):

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
    
    if self.remote_parsed.path == '/list-topics':
      return self.get_sns_listTopics()

    logger.warning("remote url not supported. Skipping: %s"%self.remote_url)
    
  def get_sns_listTopics(self):
    fn = copy.deepcopy(self.dm.fn)

    # prep inst desc
    fn['snsListTopics'] = self.dm.snsListTopics(self.my_region)
    #logger.debug("mkdir %s"%fn['snsListTopics'])
    os.makedirs(fn['snsListTopics'], exist_ok=True)

    # get instance descriptions
    logger.debug('Cloning AWS SNS list-topics')
    sns = self.session.client('sns')
    get_sns_listTopics(fn['snsListTopics'], sns)


  def capabilities(self):
    sys.stdout.write("import\n")
    
    # add refspec capability
    # treats error but I don't implement this properly
    # Copied from 
    # https://github.com/glandium/git-cinnabar/blob/9aec8ed11752ca35fe9e5581cda2b7f16aa86d0d/cinnabar/remote_helper.py#L112
    sys.stdout.write("refspec HEAD:refs/aws+sns/HEAD\n")



#-----------------

@click.command()
@click.argument('remote_name')
@click.argument('remote_url')
def cli(remote_name, remote_url):
    cli_core(remote_name, remote_url, SnsClass)


if __name__ == '__main__':
  cli()