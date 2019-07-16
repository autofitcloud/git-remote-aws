Version 0.2.0 (2019-07-16)

- FEAT: change format of remote URL so that it allows setting different endpoints
- FEAT: replace `print` with `logger.{info,debug,...}` so that the text shows up when using git
- FEAT: add ec2 catalog support (factored out some common code)
- FEAT: add logging stream to stderr
- FEAT: implement proper git <-> helper command exchange so that git no longer exits with non-0 code


Version 0.1.0 (2019-07-12)

- FEAT: initial files
- FEAT: first working version