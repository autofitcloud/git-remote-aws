from urllib.parse import urlparse
import json
import sys
import click
import os
import boto3

from .pull import SessionMan, get_instDesc
from .dotman import DotMan
import copy

class MainClass:
  def __init__(self, remote_name, remote_url):
    self.remote_name = remote_name
    self.remote_url = remote_url
    self.remote_parsed = urlparse(self.remote_url)
    
    # since the scheme is already booked for "aws+ec2",
    # including the scheme again in the hostname requires using a ~ instead of ://
    # This field treats this case.
    self.hostname_treated = None
    if self.remote_parsed.hostname is not None:
      self.hostname_treated = self.remote_parsed.hostname.replace("~", "://")
      
    if self.remote_parsed.scheme!='aws+ec2':
      raise Exception("Unsupported scheme: %s"%self.remote_parsed.scheme)

  def handle(self):
    profile_name = self.remote_parsed.username or 'default'
    
    # Debugging to file since stdout from this script does not go to terminal after git pull
    # Only the exit code survives.
    # with open('file.txt', 'w') as fp:
    #   fp.write(self.remote_parsed.hostname)
    #   fp.write("\n")
    #   fp.write(self.remote_parsed.path)
    #   fp.write("\n")

    print(self.remote_parsed.scheme)
    print(self.remote_parsed.hostname)
    print(self.remote_parsed.path)
    if self.remote_parsed.path == '/describe-instances':
      return self.get_ec2_describeInstances()

    raise Exception("remote url not supported: %s"%self.remote_url)

  def get_ec2_describeInstances(self):
    dm = DotMan()
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

    # prep inst desc
    fn['ec2DescInst'] = dm.ec2DescInst(my_region)
    #print("mkdir %s"%fn['ec2DescInst'])
    os.makedirs(fn['ec2DescInst'], exist_ok=True)
    
    # put a .gitkeep file for the sake of git add in case of empty dir
    open(os.path.join(fn['ec2DescInst'], '.gitkeep'), 'w').write('')

    # get instance descriptions
    print('Cloning AWS EC2 description data')
    ec2 = session.client('ec2', endpoint_url=self.hostname_treated)
    get_instDesc(fn, ec2)
    
    # json.dump(fn, open('file.txt','w'))


#-----------------

@click.command()
@click.argument('remote_name')
@click.argument('remote_url')
def cli(remote_name, remote_url):
    main = MainClass(sys.argv[1], sys.argv[2])
    main.handle()

if __name__ == '__main__':
  cli()
