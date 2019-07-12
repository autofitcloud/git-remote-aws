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
git remote add aws aws://profile@ec2.aws.amazon.com/describe-instances

# fetch
git fetch aws