#!/bin/sh
# Shell script demonstrating usage of git-remote-aws
# If it doesn't reach "test complete", then it must have failed early
#-------------------------

# abort on any error
set -e
set -x

# set up a git repo
REPO=`mktemp -d`
cd $REPO
git init

# add remotes
git remote add aws_ec2_describeInstances aws+ec2::/describe-instances
git remote add aws_ec2_catalog aws+ec2::/catalog
git remote add aws_cw_listMetrics aws+cw::/list-metrics
git remote add aws_cw_descAlarms aws+cw::/describe-alarms
git remote -v

# fetch
git fetch aws_ec2_describeInstances
git fetch aws_ec2_catalog
git fetch aws_cw_listMetrics
git fetch aws_cw_descAlarms

# force an error
#git remote add wrong aws+ec2://blabla/catalog
#git fetch wrong

#-------------------
tree
echo "Test complete"