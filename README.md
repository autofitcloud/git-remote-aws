# git-remote-aws [![PyPI version](https://badge.fury.io/py/git-remote-aws.svg)](https://badge.fury.io/py/git-remote-aws)

`git-remote-aws` is a [git remote helper](https://git-scm.com/docs/git-remote-helpers) for pulling data from an AWS account just like pulling from a Git remote.

Repository published on [Gitlab](https://gitlab.com/autofitcloud/git-remote-aws) and [Github](https://github.com/autofitcloud/git-remote-aws)

Website published at https://git-remote-aws.autofitcloud.com

Check the wishlist at the bottom of this readme for future plans.

<i>News 2019-08-23:</i>
I had posted this project on [r/git](https://www.reddit.com/r/git/comments/ctxcq8/gitremoteaws_aws_accounts_as_git_remotes/) last night,
only to wake up this morning and find it on top of the subreddit!
r/git is awesome!
[Screenshot](https://imgur.com/gallery/4PB2BeY)

<i>More news 2019-08-23:</i>
Apparently my cross-post to [r/aws](https://www.reddit.com/r/aws/comments/cu2llv/gitremoteaws_aws_accounts_as_git_remotes/) also made it to #3 overnight! [Screenshot](https://imgur.com/gallery/ndtJ4wc)


## Installation

```
sudo apt-get install git python3 python3-pip

pip install awscli git-remote-aws
```

## Basic Usage

Configure `awscli` with your AWS key and secret (skip this step if already done)

```
aws configure
```

The role or user for the configuration should have a subset (or all) of the following policies attached

```
AmazonEC2ReadOnlyAccess
AWSCloudTrailReadOnlyAccess
CloudWatchReadOnlyAccess
```

Init a new git repo

```
TMPDIR=`mktemp -d`
cd $TMPDIR
git init
```

Add AWS remotes for EC2 describe-instances, list-metrics, etc.

```
git remote add ctle_ec2Typechanges      aws+cloudtrail::/lookup-events?filter=ec2TypeChanges
git remote add cw_descAlarms      aws+cw::/describe-alarms
git remote add cw_getMetricData   aws+cw::/get-metric-data
git remote add cw_listMetrics     aws+cw::/list-metrics
git remote add ec2_descInstances  aws+ec2::/describe-instances
git remote add sns_listTopics     aws+sns::/list-topics
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


## Advanced Usage

### awscli profiles

To use a profile from `~/.aws/credentials` other than the default,
append `?profile=<optional profile name to use>` to the remote URLs.


### boto3 options

To append other boto3 Session constructor arguments as documented
[here](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html),
append `?boto3_session_config=path/to/file` to the remote URLs,
where `path/to/file` points to a JSON file containing the arguments from the boto3 session constructor.

For example,

```
{ "aws_access_key_id": "ABC", "aws_secret_access_key": "ABC", ...}
```


Note: The default behavior of the `describe-instances` endpoint is to subset the EC2 description to a minimal.
To get the full EC2 desriptions, append `?fulldata=true` to the endpoint.


### git push remotes

Push to a git remote

```
git add aws.amazon.com
git commit -m 'first commit'

git remote add origin git@gitlab.com:shadiakiki1986/shadiakiki1986.aws.amazon.com-json.git
git push -u origin master
```


## Covered services

The following AWS services are currently covered

Service    | Command | Notes
--------|------|------
EC2     | describe-instances | -
Cloudtrail | lookup-events | Custom filter of results for EC2 instance type changes.
Cloudwatch   | list-metrics | -
Cloudwatch   | get-metric-data | -
Cloudwatch   | describe-alarms | -
SNS | list-topics | -


Required policies/permissions per service

Service    | Policy
--------|------
EC2     | AmazonEC2ReadOnlyAccess
Cloudtrail | AWSCloudTrailReadOnlyAccess
Cloudwatch | CloudWatchReadOnlyAccess
SNS | -


### AWS/Moto endpoints

The full structure of the remote URLs is as follows

```
git remote add example_1 aws+<service>::<endpoint url>/<command>?profile=<optional profile name to use>&boto3_session_config=path/to/file
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
- `profile` is the profile name from `~/.aws/credentials`
    - Only one `profile` is supported at a time ATM, check [issue #5](https://gitlab.com/autofitcloud/git-remote-aws/issues/5)
- `boto3_session_config` is a json file of key-value pairs corresponding to boto3 session constructor arguments
    - this is optional
    - documentation for boto3 session is [here](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html)
    - Only one `boto3_session_config` is supported at a time ATM, check [issue #5](https://gitlab.com/autofitcloud/git-remote-aws/issues/5)


Examples

```
# get from AWS using the default profile in ~/.aws/credentials
git remote add example_1_ec2 aws+ec2::/describe-instances
git remote add example_1_catalog aws+ec2::/catalog
git remote add example_1_cwListMetrics aws+cw::/list-metrics

# Specific aws endpoint
git remote add example_3 aws+ec2::http://ec2.us-west-2.amazonaws.com/describe-instances

# use a specific profile and AWS default endpoints
git remote add example_2 aws+ec2::/describe-instances?profile_name=profile&boto3_session_config=path/to/file
```

Pull the data

```
git fetch example_1_ec2
git fetch example_1_catalog
```


## Developer notes

Check `DEVELOPER.md`


## Wishlist

Here is a list of features that were brought up from reddit [r/git](https://www.reddit.com/r/git/comments/ctxcq8/gitremoteaws_aws_accounts_as_git_remotes/exsu7bs/?context=3) and [r/aws](https://www.reddit.com/r/aws/comments/cu2llv/gitremoteaws_aws_accounts_as_git_remotes/)

- [Issue #1](https://github.com/autofitcloud/git-remote-aws/issues/1): Add push capability to the aws+ec2://describe-instances remote
- [Issue #2](https://github.com/autofitcloud/git-remote-aws/issues/2): git fetch should build a history when possible


## Support

I built `git-remote-aws` as part of the workflow behind [AutofitCloud](https://autofitcloud.com), the early-stage startup that I'm founding, seeking to cut cloud waste on our planet.

If you like `git-remote-aws` and would like to see it developed further,
please support me by signing up at https://autofitcloud.com

Over and out!

--[u/shadiakiki1986](https://www.reddit.com/user/shadiakiki1986)
