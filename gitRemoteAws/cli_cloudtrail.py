# RuntimeError: Click will abort further execution because Python 3 was configured to use ASCII as encoding for the environment. 
# Consult https://click.palletsprojects.com/en/7.x/python3/ for mitigation steps.
from .utils import mysetlocale
mysetlocale()

#---------------

import os
from urllib.parse import urlparse
import json
import sys
import click
import boto3
import logging

from .cli_ec2 import Ec2Class, cli_core
# from .pull import SessionMan
from .pull_cloudtrail_lookupEvents import GeneralManager as LookupeventsManager
from .dotman import DotMan
import copy

logger = logging.getLogger('git-remote-aws')

class CloudtrailClass(Ec2Class):

  def list(self):
    logger.debug('cloudtrailclass.list')
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
    
    if self.remote_parsed.path == '/lookup-events':
      return self._lookupEvents()
      
    logger.warning("remote url not supported. Skipping: %s"%self.remote_url)
    

  def _lookupEvents(self):
    fn = copy.deepcopy(self.dm.fn)

    # prep inst desc
    dirroot = self.dm.cloudtrailLookupEvents(self.my_region)
    #logger.debug("mkdir %s"%dirroot)
    os.makedirs(dirroot, exist_ok=True)
    
    dirEc2TypeChanges = os.path.join(dirroot, "ec2TypeChanges")
    os.makedirs(dirEc2TypeChanges, exist_ok=True)

    # get instance descriptions
    cloudtrail = self.session.client('cloudtrail')
    man3 = LookupeventsManager(cloudtrail)

    # identify filter
    filterName = self.get_qs_first('filter')
    if filterName=='ec2TypeChanges':
      # get instance descriptions
      logger.debug('Cloning AWS Cloudtrail lookup-events for ec2 type changes')

      df_all = man3.ec2_typeChanges()
        
      # list of instance IDs
      iid_all = set(df_all.reset_index()['instanceId'].tolist())
      for instance_id in iid_all:
        df_sub = df_all.loc[instance_id]
        csvName = os.path.join(dirroot, "ec2TypeChanges", instance_id + ".csv")
        df_sub.to_csv(csvName)
        
      return # done

    logger.warning("filter not supported. Skipping: %s"%filterName)



  def capabilities(self):
    sys.stdout.write("import\n")
    
    # add refspec capability
    # treats error but I don't implement this properly
    # Copied from 
    # https://github.com/glandium/git-cinnabar/blob/9aec8ed11752ca35fe9e5581cda2b7f16aa86d0d/cinnabar/remote_helper.py#L112
    sys.stdout.write("refspec HEAD:refs/aws+cloudtrail/HEAD\n")



#-----------------

@click.command()
@click.argument('remote_name')
@click.argument('remote_url')
def cli(remote_name, remote_url):
    cli_core(remote_name, remote_url, CloudtrailClass)


if __name__ == '__main__':
  cli()
