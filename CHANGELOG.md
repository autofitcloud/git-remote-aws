Version latest (0.5.1) (2019-08-30?)

- ...


Version 0.5.1 (2019-08-30)

- FEAT: use RunInstance event name on top of ModifyInstanceAttribute to get the initial instance type


Version 0.5.0 (2019-08-30)

- FEAT: add cloutrail endpoint for lookup-events with custom filter for ec2 type changes


Version 0.4.0 (2019-08-15)

- FEAT: replace `profile_name` in git remote URL with `boto3_session_kwargs` (JSON containing `profile_name` as one of the keys)
- BUGFIX: bring back `profile_name` and replace `boto3_session_kwargs` with `boto3_session_config` (JSON file for shorter URLs)
- ENH: comment out downloading hourly CPU


Version 0.3.9 (2019-08-{08,14})

- ENH: add cases to test
- ENH: improve docs
- BUGFIX: check for locale before setting it (faced when deploying on AWS lambda)
- bugfix: cancel 0.3.8


Version 0.3.7 (2019-08-08)

- ENH: add feature `?fulldata=true` to the `ec2_describeInstances` endpoint
    - this followed from strong criticism on reddit in my post: [Is opensource infrastructure safe?](https://www.reddit.com/r/aws/comments/cn81my/is_opensource_infrastructure_safe/)


Version 0.3.6 (2019-08-07)

- ENH: moved path of aws catalog from gitRemoteAws.pull into dotman.fn.awsCat
- BUGFIX: refactor `df` to `df_pd` to distnguish from `df_json` in `pull`
- BUGFIX: flattening the `pricing` field from `www.ec2instance.info` was yielding NaN. Replaced with the average price of all regions.


Version 0.3.5 (2019-08-07)

- ENH: readme cleanup
- ENH: split out developer notes to separate file than README.md
- released on pypi


Version 0.3.4 (2019-08-07)

- ENH: add description in setup.py


Version 0.3.3 (2019-08-07)

- ENH: change aws data root to be aws.amazon.com instead of just aws
- ENH: improved readme


Version 0.3.2 (2019-08-06)

- ENH: add progress output (still pending including a percentage, check issue # 6) with tqdm
- BUGFIX: comment out logger.setLevel (should be based on the -v, check issue # 7)
- BUGFIX: increase maxresults in fetch aws+ec2 instance descriptions from 30 to 3000 + add warning when the limit is hit


Version 0.3.1 (2019-08-02)

- BUGFIX: fix wrong variable reference
- FEAT: implement the `profile_name` parameter


Version 0.3.0 (2019-07-22)

- FEAT: add sns list-topics


Version 0.2.1 (2019-07-18)

- FEAT: drop deprecated piece of code in pull.py that was moved into `cli_*.py`
- FEAT: use jmespath in filtering the cloudwatch describe alarms response
- FEAT: implement cloudwatch list-metrics remote fetch
- FEAT: implement cloudwatch get-metric-data
- ENH: move `cw_getMetricStatistics` out of ec2op to here for later integration (check issue #4)
- ENH: use package name "git-remote-aws" with dashes instead of "gitRemoteAws" in setup.py
- ENH: add locale at top of cli.py files
- ENH: ec2 catalog coming from non-aws source to go into separate folder than aws subrepo
- BUGIFX: include statistic in folder name of get-metric-data


Version 0.2.0 (2019-07-16)

- FEAT: change format of remote URL so that it allows setting different endpoints
- FEAT: replace `print` with `logger.{info,debug,...}` so that the text shows up when using git
- FEAT: add ec2 catalog support (factored out some common code)
- FEAT: add logging stream to stderr
- FEAT: implement proper git <-> helper command exchange so that git no longer exits with non-0 code
- ENH: factor out `cli` to `cli_core` and `Ec2Class` in preparation for new `aws+cw` protocol
- FEAT: factor out and add alternative command for cloudwatch
- FEAT: add cloudwatch/describe-alarms



Version 0.1.0 (2019-07-12)

- FEAT: initial files
- FEAT: first working version
