# git-remote-aws

git remote helper for pulling aws data

Published at https://gitlab.com/autofitcloud/git-remote-aws


## Installation

```
sudo apt-get install git python3 python3-pip

pip install awscli git-remote-aws
```

## Usage

Configure `awscli` with your AWS key and secret (skip this step if already done)

```
aws configure
```

Init a new git repo

```
TMPDIR=`mktemp -d`
cd $TMPDIR
git init
```

Add AWS remotes for EC2 describe-instances, list-metrics, etc.. To use a profile from `~/.aws/credentials` other than the default,
append `?profile_name=<optional profile name to use>` to the remote URLs below.

```
git remote add ec2_descInstances  aws+ec2::/describe-instances
git remote add cw_listMetrics     aws+cw::/list-metrics
git remote add sns_listTopics     aws+sns::/list-topics
git remote add cw_getMetricData   aws+cw::/get-metric-data
git remote add cw_descAlarms      aws+cw::/describe-alarms
```

Fetch data from all remotes.

```
git fetch --all
```

This creates a folder `aws.amazon.com` with a directory structure containing the relevant data

```
> tree
.
└── aws.amazon.com
    └── us-west-2
        └── ec2_describeInstances
        │   ├── i-02432bc7.json
        │   ├── i-069a7808addd143c7.json
        │   ├── i-08c802de5accc1e89.json
        │   ├── i-0e2662888859c5507.json
        │   ├── i-0fb05d874895a05ec.json
        │   ├── i-34ca2fc2.json
        │   └── i-e1ca46eb.json
        └── ...

4 directories, 11 files
```

Publish your [open-source infrastructure](https://opensourceinfra.org/)

```
git add aws.amazon.com
git commit -m 'first commit'

git remote add origin git@gitlab.com:shadiakiki1986/shadiakiki1986.aws.amazon.com-json.git
git push -u origin master
```

## Advanced

The full structure of the remote URLs is as follows

```
git remote add example_1 aws+<service>::<endpoint url>/<command>?profile_name=<optional profile name to use>
```

where

- `service` is one of: `ec2`, `cw` (cloudwatch), `sns`
- `endpoint url` is the AWS endpoint to use
    - leave blank for the default AWS endpoints, or use [moto](http://docs.getmoto.org/en/latest/) for mocked AWS services
- `command`: depending on the `service` above, this can be
    - `ec2`:
        - `describe-instances`
        - `catalog` (this is not an official AWS service, but is populated from https://www.ec2instances.info. Check related note in "Developer notes" below)
    - `cw`:
        - `list-metrics`
        - `get-metric-data`
        - `describe-alarms`
    - `sns`
        - `list-topics`
- `profile_name` is the profile name from `~/.aws/credentials`
    - this is optional
    - Only one profile supported at a time (ATM, check [issue #5](https://gitlab.com/autofitcloud/git-remote-aws/issues/5))


Examples

```
# get from AWS using the default profile in ~/.aws/credentials
git remote add example_1_ec2 aws+ec2::/describe-instances
git remote add example_1_catalog aws+ec2::/catalog
git remote add example_1_cwListMetrics aws+cw::/list-metrics

# Specific aws endpoint
git remote add example_3 aws+ec2::http://ec2.us-west-2.amazonaws.com/describe-instances

# use a specific profile and AWS default endpoints
git remote add example_2 aws+ec2::profile@/describe-instances
```

Pull the data

```
git fetch example_1_ec2
git fetch example_1_catalog
```


## Developer notes

Check `DEVELOPER.md`