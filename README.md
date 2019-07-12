# git-remote-aws

git remote helper for pulling aws data

https://git-scm.com/docs/gitremote-helpers


## Installation

```
pip install git+https://...
```

## Usage

```
cd /tmp
mkdir bla
cd bla
git init
git remote add ec2DescInst aws://describe-instances.ec2.aws.amazon.com
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
