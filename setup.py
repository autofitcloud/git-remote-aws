from setuptools import setup, find_packages

setup(
    name='gitRemoteAws',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'boto3',
        'click',
        'requests',
        'cachecontrol',
        'pandas',
        'pyyaml==5.1.1',
    ],
    entry_points='''
        [console_scripts]
        git-remote-aws+ec2=gitRemoteAws.main:cli
    ''',
)
