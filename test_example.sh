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
git remote add aws_ec2_describeInstances_1 aws+ec2::/describe-instances
git remote add aws_ec2_describeInstances_2 aws+ec2::/describe-instances?profile=default # try with the profile passing
git remote add aws_ec2_describeInstances_3a aws+ec2::/describe-instances?fulldata=false # without fulldata (already the default)
git remote add aws_ec2_describeInstances_3b aws+ec2::/describe-instances?fulldata=true # with fulldata
git remote add aws_ec2_catalog aws+ec2::/catalog
git remote add aws_cw_listMetrics aws+cw::/list-metrics
git remote add aws_cw_descAlarms aws+cw::/describe-alarms
git remote add aws_cw_getMetricData aws+cw::/get-metric-data
git remote add aws_sns_listTopics aws+sns::/list-topics
git remote add aws_ctle_ec2TypeChanges aws+cloudtrail::/lookup-events?filter=ec2TypeChanges
git remote add aws_ctle_ec2TypeChanges "aws+cloudtrail::/lookup-events?filter=ec2TypeChanges&profile=shadi_none" # region with no ec2 instances
git remote -v

# fetch individually or all
# git fetch aws_ec2_describeInstances_1
# git fetch aws_ec2_catalog
# git fetch aws_cw_listMetrics
# git fetch aws_cw_descAlarms
# git fetch aws_cw_getMetricData
# git fetch aws_sns_listTopics
git fetch --all

# force an error
#git remote add wrong aws+ec2://blabla/catalog
#git fetch wrong

#-------------------
tree
echo "Test complete"
