# RuntimeError: Click will abort further execution because Python 3 was configured to use ASCII as encoding for the environment. 
# Consult https://click.palletsprojects.com/en/7.x/python3/ for mitigation steps.
import os
os.environ["LC_ALL"] = "C.UTF-8"
os.environ["LANG"]   = "C.UTF-8"


from urllib.parse import urlparse, parse_qs
import json
import sys
import click
import boto3
import logging

from .botoman import SessionMan
from .pull import get_instDesc, get_awsCat, get_cwDescAlarms
from .dotman import DotMan
import copy

logger = logging.getLogger('git-remote-aws')

class Ec2Class:
  def __init__(self, remote_name, remote_url):
    self.remote_name = remote_name
    self.remote_url = remote_url
    
    # git will drop the aws+ec2:: prefix before passing the remote URL
    # https://rovaughn.github.io/2015-2-9.html
    # if not remote_url.startswith('aws+ec2::'):
    #   raise Exception("Unsupported git protocol: %s"%remote_url)
    
    # parse  with urllib
    # Example
    # >>> from urllib.parse import urlparse, parse_qs
    # >>> x='/describe-instances?profile=default&foo=bar'
    # >>> urlparse(x)
    # ParseResult(scheme='', netloc='', path='/describe-instances', params='', query='profile=default&foo=bar', fragment='')
    # >>> parse_qs(urlparse(x).query)
    # {'profile': ['default'], 'foo': ['bar']}
    self.remote_parsed = urlparse(self.remote_url)
    
    # parse query
    self.remote_query = parse_qs(self.remote_parsed.query)
    
    # since the scheme is already booked for "aws+ec2",
    # including the scheme again in the hostname requires using a ~ instead of ://
    # This field treats this case.
    self.endpoint_url = None
    if self.remote_parsed.hostname is not None:
      self.endpoint_url = "%s://%s"%(self.remote_parsed.scheme, self.remote_parsed.hostname)

    # more class members
    self.dm = DotMan()

    # identify profile name from remote query
    profile_name = None
    if 'profile_name' in self.remote_query:
      if len(self.remote_query['profile_name'])>0:
        # only take the first entry ATM, check https://gitlab.com/autofitcloud/git-remote-aws/issues/5
        profile_name=self.remote_query['profile_name'][0] 
    
    # get region https://stackoverflow.com/a/37519906/4126114
    self.session = SessionMan(self.dm, profile_name=profile_name)
    self.my_region = self.session.getSession().region_name
    #region_name is basically defined as session.get_config_variable('region')
    # logger.debug("sts region", my_region)
    
    if self.my_region is None:
        logger.error("fatal: failed to detect region name.")
        logger.error("Are you sure you configured awscli? Check files in %s"%self.dm.fn['aws_dot'])
        sys.exit(1)



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
    
    logger.debug("parsed query")
    logger.debug(self.remote_query)
    
    # mkdir as needed
    self.makedirsRegion()
    
    if self.remote_parsed.path == '/describe-instances':
      return self.get_ec2_describeInstances()
      
    if self.remote_parsed.path=='/catalog':
      return self.get_ec2_catalog()

    logger.warning("remote url not supported. Skipping: %s"%self.remote_url)


  def makedirsRegion(self):
    fn = copy.deepcopy(self.dm.fn)

    fn['pull_region_one'] = self.dm.pull_region_one(self.my_region)
    #logger.debug("makedirsRegion %s"%fn['pull_region_one'])
    os.makedirs(fn['pull_region_one'], exist_ok=True)


  def get_ec2_describeInstances(self):
    fn = copy.deepcopy(self.dm.fn)
    
    # prep inst desc
    fn['ec2DescInst'] = self.dm.ec2DescInst(self.my_region)
    #logger.debug("makedirsRegion %s"%fn['ec2DescInst'])
    os.makedirs(fn['ec2DescInst'], exist_ok=True)
    
    # put a .gitkeep file for the sake of git add in case of empty dir
    open(os.path.join(fn['ec2DescInst'], '.gitkeep'), 'w').write('')

    # get instance descriptions
    logger.info('Cloning AWS EC2 description data\n')
    try:
      ec2 = self.session.client('ec2', endpoint_url=self.endpoint_url)
    except ValueError as error:
      sys.stderr.write("fatal: %s\n"%str(error))
      sys.exit(70) # internal program error, https://github.com/glandium/git-cinnabar/blob/master/cinnabar/util.py#L916
      
    get_instDesc(fn, ec2)
    
    # json.dump(fn, open('file.txt','w'))
    
  
  def get_ec2_catalog(self):
    fn = copy.deepcopy(self.dm.fn)
    logger.info('Fetching aws ec2 catalog')
    get_awsCat(fn)
    
  def capabilities(self):
    sys.stdout.write("import\n")
    
    # add refspec capability
    # treats error but I don't implement this properly
    # Copied from 
    # https://github.com/glandium/git-cinnabar/blob/9aec8ed11752ca35fe9e5581cda2b7f16aa86d0d/cinnabar/remote_helper.py#L112
    sys.stdout.write("refspec HEAD:refs/aws+ec2/HEAD\n")



#-----------------
def cli_core(remote_name, remote_url, HandlerClass):
    """
    HandlerClass - eg Ec2Class, CwClass
    """
    
    # init logging .. it's very important to use the stdout streamhandler so that git doesn't return a non-0 exit code
    ch = logging.StreamHandler(sys.stderr)
    # TODO figure out how the `-v` in `git fetch remotename -v` is passed, and use it to increase the level below
    # logger.setLevel(logging.DEBUG) # DEBUG WARNING
    logger.addHandler(ch)
    
    # start
    logger.info('Fetching from name, url: %s, %s\n'%(remote_name, remote_url))
    
    while True:
      # check if git is requesting capabilities
      # https://click.palletsprojects.com/en/5.x/utils/#standard-streams
      # cmd = click.get_text_stream('stdin')
      cmd = sys.stdin.readline().strip() # strip to remove trailing new-line character
      if cmd=='import': cmd='import_' # since import is not allowed
      logger.debug('stdin is "%s"'%cmd)

      if cmd=='':
        break
       
      main = HandlerClass(remote_name, remote_url)
      func = getattr(main, cmd, None)
      if func is None:
        raise Exception("Unsupported command %s"%cmd)
    
      # call command             
      func()
      # copied idea of new-line and flush from
      # https://github.com/glandium/git-cinnabar/blob/9aec8ed11752ca35fe9e5581cda2b7f16aa86d0d/cinnabar/remote_helper.py#L115
      sys.stdout.write("\n")
      sys.stdout.flush()
      continue


@click.command()
@click.argument('remote_name')
@click.argument('remote_url')
def cli(remote_name, remote_url):
    cli_core(remote_name, remote_url, Ec2Class)


if __name__ == '__main__':
  cli()