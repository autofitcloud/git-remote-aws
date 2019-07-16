#!/bin/sh
# Shell script demonstrating usage of git-remote-aws
#-------------------------

# abort on any error
set -e

# set up a git repo
REPO=`mktemp -d`
cd $REPO
git init

# add remote
git remote add aws_ec2 aws+ec2:///describe-instances

# fetch
git fetch aws_ec2


echo "Test complete"