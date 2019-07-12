# git-remote-aws

git remote helper for pulling aws data

https://git-scm.com/docs/gitremote-helpers


## Installation

```
sudo apt-get install git python3 python3-pip
pip3 install git+https://gitlab.com/autofitcloud/git-remote-aws.git@0.1.0
```

## Usage

Add a `aws://...` remote

```
cd /tmp
mkdir bla
cd bla
git init
git remote add aws aws://profile@ec2.aws.amazon.com/describe-instances
```

Fetch the data

```
git fetch aws
```

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