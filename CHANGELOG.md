Version 0.2.1 (2019-07-18)

- FEAT: drop deprecated piece of code in pull.py that was moved into cli_*.py
- FEAT: use jmespath in filtering the cloudwatch describe alarms response
- FEAT: implement cloudwatch list-metrics remote fetch
- FEAT: implement cloudwatch get-metric-data
- ENH: move cw_getMetricStatistics out of ec2op to here for later integration (check issue #4)
- ENH: use package name "git-remote-aws" with dashes instead of "gitRemoteAws" in setup.py
- ENH: add locale at top of cli.py files


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