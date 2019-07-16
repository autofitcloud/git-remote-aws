from urllib.parse import urlparse
import json
import sys
import click
import os
import boto3
import logging

from .pull import SessionMan, get_instDesc, get_awsCat
from .dotman import DotMan
import copy

logger = logging.getLogger('git-remote-aws')

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
      
    # more class members
    self.dm = DotMan()

    # get region https://stackoverflow.com/a/37519906/4126114
    self.session = SessionMan(self.dm)
    self.my_region = self.session.getSession().region_name
    #region_name is basically defined as session.get_config_variable('region')
    # logger.debug("sts region", my_region)
    
    if self.my_region is None:
        logger.error("fatal: failed to detect region name.")
        logger.error("Are you sure you configured awscli? Check files in %s"%dm.fn['aws_dot'])
        sys.exit(1)



  def handle(self):
    profile_name = self.remote_parsed.username or 'default'
    
    # Debugging to file since stdout from this script does not go to terminal after git pull
    # Only the exit code survives.
    # with open('file.txt', 'w') as fp:
    #   fp.write(self.remote_parsed.hostname)
    #   fp.write("\n")
    #   fp.write(self.remote_parsed.path)
    #   fp.write("\n")

    # logger.debug(self.remote_parsed.scheme)
    # logger.debug(self.remote_parsed.hostname)
    # logger.debug(self.remote_parsed.path)
    
    self.mkdir()
    
    if self.remote_parsed.path == '/describe-instances':
      return self.get_ec2_describeInstances()
      
    if self.remote_parsed.path=='/catalog':
      return self.get_ec2_catalog()

    raise Exception("remote url not supported: %s"%self.remote_url)


  def mkdir(self):
    fn = copy.deepcopy(self.dm.fn)

    fn['pull_region_one'] = self.dm.pull_region_one(self.my_region)
    #logger.debug("mkdir %s"%fn['pull_region_one'])
    os.makedirs(fn['pull_region_one'], exist_ok=True)


  def get_ec2_describeInstances(self):
    fn = copy.deepcopy(self.dm.fn)
    
    # prep inst desc
    fn['ec2DescInst'] = self.dm.ec2DescInst(self.my_region)
    #logger.debug("mkdir %s"%fn['ec2DescInst'])
    os.makedirs(fn['ec2DescInst'], exist_ok=True)
    
    # put a .gitkeep file for the sake of git add in case of empty dir
    open(os.path.join(fn['ec2DescInst'], '.gitkeep'), 'w').write('')

    # get instance descriptions
    logger.info('Cloning AWS EC2 description data\n')
    try:
      ec2 = self.session.client('ec2', endpoint_url=self.hostname_treated)
    except ValueError as error:
      sys.stderr.write("fatal: %s\n"%str(error))
      sys.exit(70) # internal program error, https://github.com/glandium/git-cinnabar/blob/master/cinnabar/util.py#L916
      
    get_instDesc(fn, ec2)
    
    # json.dump(fn, open('file.txt','w'))
    
  
  def get_ec2_catalog(self):
    fn = copy.deepcopy(self.dm.fn)
    get_awsCat(fn)


#-----------------

@click.command()
@click.argument('remote_name')
@click.argument('remote_url')
def cli(remote_name, remote_url):
    # init logging .. it's very important to use the stdout streamhandler so that git doesn't return a non-0 exit code
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    logger.addHandler(ch)
    
    # start
    logger.info('Fetching from %s\n'%remote_url)
    
    # check if git is requesting capabilities
    # https://click.palletsprojects.com/en/5.x/utils/#standard-streams
    # stdin_text = click.get_text_stream('stdin')
    # logger.debug('stdin is')
    # logger.debug(stdin_text.read())
    # logger.debug('')
    # if stdin_text=='capabilities':
    #   logger.debug("import")
    #   return
  
    # proceed
    main = MainClass(sys.argv[1], sys.argv[2])
    main.handle()


if __name__ == '__main__':
  cli()
