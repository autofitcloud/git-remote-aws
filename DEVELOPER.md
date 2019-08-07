# git-remote-aws

## Developer notes

PS: `git fetch aws` will actually create the files in the local directory (unlike a normal `git fetch` which doesn't update the local files)

Save into a subdirectory (doesnt work yet)

```
mkdir ec2DescInst
git worktree add ec2DescInst example_1
```

Install editable python package

```
pip install pew
pew new test_gra
# needed? # pip3 install -r requirements.txt
pip3 install -e .
```

Test

```
echo "list" | git-remote-aws+ec2 aws /describe-instances # default AWS endpoint
echo "list" | git-remote-aws+ec2 aws http://ec2.us-west-2.amazonaws.com/describe-instances # specific AWS endpoint
echo "list" | git-remote-aws+ec2 aws http://localhost:5000/describe-instances # moto AWS endpoint
```

or more completely

```
bash test_example.sh
```

Testing against [moto server](https://github.com/spulec/moto#stand-alone-server-mode)

```
pip3 install "moto[server]"
moto_server ec2 -p3000

echo "list" | git-remote-aws+ec2 aws http://localhost:3000/describe-instances
```

or

```
git init
git remote add aws aws+ec2::http://localhost:3000/describe-instances
git fetch aws
```


References for git remote helpers

- https://git-scm.com/docs/gitremote-helpers
- https://github.com/git/git/blob/master/t/t5801/git-remote-testgit
- https://github.com/search?utf8=%E2%9C%93&q=git%2Dremote%2Dhelper
    - list of git remote helpers on github.com
- https://rovaughn.github.io/2015-2-9.html
    - https://github.com/rovaughn/git-remote-grave
    - this is a go implementation, but the accompanying blog post is very explanatory
- https://github.com/glandium/git-cinnabar/blob/9aec8ed11752ca35fe9e5581cda2b7f16aa86d0d/cinnabar/remote_helper.py#L112
    - this is a python implementation
- https://github.com/awslabs/git-remote-codecommit


Publish to pypi

```
python3 setup.py sdist bdist_wheel
twine upload dist/*
```


Install git-remote-aws from gitlab

```
# over ssh if private repo
pip3 install git+ssh://git@gitlab.com/autofitcloud/git-remote-aws.git@0.1.0

# over https if public repo
pip3 install git+https://gitlab.com/autofitcloud/git-remote-aws.git@0.1.0
```

To get AWS EC2 catalog (generates a 23MB file `www.ec2instances.info/t0_raw.json`)

```
git remote add ec2_catalog        aws+ec2::/catalog
git fetch ec2_catalog

echo "www.ec2instances.info/t0_raw.json" > .gitignore # useful to avoid checking in a 23MB file
```