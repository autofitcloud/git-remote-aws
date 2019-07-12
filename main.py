# import boto3
from urllib.parse import urlparse
import json
import sys
class MainClass:
  def __init__(self, remote_name, remote_url):
    self.remote_name = remote_name
    self.remote_url = remote_url
    self.remote_parsed = urlparse(self.remote_url)
    if self.remote_parsed.scheme!='aws':
      raise Exception("Unsupported scheme: %s"%remote_parsed.scheme)

  def handle(self):
    profile_name = self.remote_parsed.username or 'default'
    if self.remote_parsed.hostname == 'ec2.aws.amazon.com':
      if self.remote_parsed.path == 'describe-instances':
        self.get_ec2_describeInstances()

    raise Exception("remote url not supported: %s"%remote_url)

  def get_ec2_describeInstances(self):
    dummy={'foo':'bar'}
    json.dump('file.txt', dummy)


#-----------------

import click

@click.command()
@click.argument('remote_name')
@click.argument('remote_url')
def cli(remote_name, remote_url):
    main = MainClass(sys.argv[1], sys.argv[2])
    main.handle()

if __name__ == '__main__':
  cli()
