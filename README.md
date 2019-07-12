# git-remote-aws

git remote helper for pulling aws data

https://git-scm.com/docs/gitremote-helpers


## Installation

```
apt-get install git
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

```
sudo apt-get install python3 python3-pip
pip install pew
pew new test_gra
pip install -r requirements.txt

```
