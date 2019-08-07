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

PS: `git fetch aws` will actually create the files in the local directory (unlike a normal `git fetch` which doesn't update the local files)

Save into a subdirectory (doesnt work yet)

```
mkdir ec2DescInst
git worktree add ec2DescInst example_1
```

Install editable python package

```
pip install pew
pew new test_gra
# needed? # pip3 install -r requirements.txt
pip3 install -e .
```

Test

```
echo "list" | git-remote-aws+ec2 aws /describe-instances # default AWS endpoint
echo "list" | git-remote-aws+ec2 aws http://ec2.us-west-2.amazonaws.com/describe-instances # specific AWS endpoint
echo "list" | git-remote-aws+ec2 aws http://localhost:5000/describe-instances # moto AWS endpoint
```

or more completely

```
bash test_example.sh
```

Testing against [moto server](https://github.com/spulec/moto#stand-alone-server-mode)

```
pip3 install "moto[server]"
moto_server ec2 -p3000

echo "list" | git-remote-aws+ec2 aws http://localhost:3000/describe-instances
```

or

```
git init
git remote add aws aws+ec2::http://localhost:3000/describe-instances
git fetch aws
```


References for git remote helpers

- https://git-scm.com/docs/gitremote-helpers
- https://github.com/git/git/blob/master/t/t5801/git-remote-testgit
- https://github.com/search?utf8=%E2%9C%93&q=git%2Dremote%2Dhelper
    - list of git remote helpers on github.com
- https://rovaughn.github.io/2015-2-9.html
    - https://github.com/rovaughn/git-remote-grave
    - this is a go implementation, but the accompanying blog post is very explanatory
- https://github.com/glandium/git-cinnabar/blob/9aec8ed11752ca35fe9e5581cda2b7f16aa86d0d/cinnabar/remote_helper.py#L112
    - this is a python implementation
- https://github.com/awslabs/git-remote-codecommit


Publish to pypi

```
python3 setup.py sdist bdist_wheel
twine upload dist/*
```


Install git-remote-aws from gitlab

```
# over ssh if private repo
pip3 install git+ssh://git@gitlab.com/autofitcloud/git-remote-aws.git@0.1.0

# over https if public repo
pip3 install git+https://gitlab.com/autofitcloud/git-remote-aws.git@0.1.0
```

To get AWS EC2 catalog (generates a 23MB file `www.ec2instances.info/t0_raw.json`)

```
git remote add ec2_catalog        aws+ec2::/catalog
git fetch ec2_catalog

echo "www.ec2instances.info/t0_raw.json" > .gitignore # useful to avoid checking in a 23MB file
```