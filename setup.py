from setuptools import setup # , find_packages

# follow https://github.com/awslabs/git-remote-codecommit/blob/master/setup.py
# and https://packaging.python.org/tutorials/packaging-projects/
setup(
    name='git-remote-aws',
    version='0.3.3',
    author="AutofitCloud Technologies, Inc",
    author_email="shadi@autofitcloud.com",
    url='https://gitlab.com/autofitcloud/git-remote-aws',
    
    # packages=find_packages(),
    packages = ['gitRemoteAws'],
    include_package_data=True,
    install_requires=[
        'boto3',
        'click',
        'requests',
        'cachecontrol',
        'pandas',
        'pyyaml==5.1.1',
        'jmespath==0.9.4',
        'tqdm==4.32.2',
    ],
    entry_points='''
        [console_scripts]
        git-remote-aws+ec2=gitRemoteAws.cli_ec2:cli
        git-remote-aws+cw=gitRemoteAws.cli_cw:cli
        git-remote-aws+sns=gitRemoteAws.cli_sns:cli
    ''',
)
