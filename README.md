# git-remote-aws

git remote helper for pulling aws data

https://git-scm.com/docs/gitremote-helpers


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
git remote add aws aws://profile@ec2.aws.amazon.com/describe-instances
```

Pull the data

```
git pull aws
```

This creates a folder "aws" with a directory structure containing the relevant data

```
> tree
.
└── aws
    └── us-west-2
        └── ec2_describeInstances
            ├── i-02432bc7.json
            ├── i-069a7808addd143c7.json
            ├── i-08c802de5accc1e89.json
            ├── i-0e2662888859c5507.json
            ├── i-0fb05d874895a05ec.json
            ├── i-34ca2fc2.json
            └── i-e1ca46eb.json

3 directories, 7 files
```

## Notes

PS: `git fetch aws` will also just pull ATM

Save into a subdirectory

```
mkdir ec2DescInst
git worktree add ec2DescInst ec2DescInst
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
git-remote-aws aws aws://profile@ec2.aws.amazon.com/describe-instances
```

or more completely

```
bash test_example.sh
```