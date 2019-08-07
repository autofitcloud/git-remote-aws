# git-remote-aws

git remote helper for pulling aws data

Published at https://gitlab.com/autofitcloud/git-remote-aws


## Installation

```
sudo apt-get install git python3 python3-pip

# over ssh if private repo
pip3 install git+ssh://git@gitlab.com/autofitcloud/git-remote-aws.git@0.1.0

# over https if public repo
pip3 install git+https://gitlab.com/autofitcloud/git-remote-aws.git@0.1.0
```

## Usage

Init a new git repo

```
mktemp -d
cd path/from/above
git init
```

Add the aws remote for ec2 describe-instances

```
git remote add example_1 aws+<service>::<endpoint url>/<command>?profile_name=<optional profile name to use>
```

where

- `service` is one of: `ec2`, `cw` (cloudwatch)
- `endpoint url` is the AWS endpoint to use (leave blank for the default, or check examples below)
- `command` can be one of
    - `describe-instances`
    - `catalog`
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

This creates a folder "aws" with a directory structure containing the relevant data

```
> tree
.
└── aws
    ├── us-west-2
    │   └── ec2_describeInstances
    │       ├── i-02432bc7.json
    │       ├── i-069a7808addd143c7.json
    │       ├── i-08c802de5accc1e89.json
    │       ├── i-0e2662888859c5507.json
    │       ├── i-0fb05d874895a05ec.json
    │       ├── i-34ca2fc2.json
    │       └── i-e1ca46eb.json
    └── www.ec2instances.info
        ├── t0_raw.json
        ├── t1_processed.json
        ├── t3a_smaller_familyL1.json
        └── t3b_smaller_familyL2.json

4 directories, 11 files
```

## Notes

PS: `git fetch aws` will actually create the files in the local directory (unlike a normal `git fetch` which doesn't update the local files)

Save into a subdirectory (doesnt work yet)

```
mkdir ec2DescInst
git worktree add ec2DescInst example_1
```

For more data
```
git remote add ec2GetMetrics aws://get-metrics.ec2.aws.amazon.com
git remote add cwDescAlarms aws://describe-alarms.cw.aws.amazon.com

mkdir ec2GetMetrics
mkdir cwDescAlarms
```


## Developer notes

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