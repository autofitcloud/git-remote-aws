"""
Wrappers for boto3 calls
"""

import boto3
import yaml
import os
from botocore.exceptions import ProfileNotFound
import sys

class SessionMan:
    """
    Manager of boto3 calls
    """
    def __init__(self, dm=None):
        """
        dm - instance of dotman.DotMan
        """
        self.dm = dm

    def getSession(self, profile_name=None):
        """
        Wrap call to "boto3.session" to pass profile from config
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html?highlight=boto3.session.session.client#boto3.session.Session.client

        Also
        https://stackoverflow.com/a/42818143/4126114
        """
        try:
            return boto3.session.Session(profile_name=profile_name)
        except ProfileNotFound as error:
            print("fatal: %s"%str(error))

            # if not at clone stage
            if self.dm is not None:
                print("Perhaps edit the 'profile' field in %s"%self.dm.fn['config'])
                print("to match with the profiles in %s"%self.dm.fn['aws_credentials'])

            sys.exit(1)

    def client(self, service_name, profile_name=None, endpoint_url=None):
        session = self.getSession(profile_name=profile_name)
        client = session.client(service_name, endpoint_url=endpoint_url)
        return client