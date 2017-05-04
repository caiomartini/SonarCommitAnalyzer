# SonarCommit ![logo](https://s3-ap-northeast-1.amazonaws.com/qiita-tag-image/acaa785eea912847ad246c30f4673f58f8748882/medium.jpg?1468193129)
Code analysing with SonarQube in pre-commit.

### Pre requirements
- Git
- Python 3.6.1
- SonarQube

### Python libraries pre requirements
- [GitPython](https://gitpython.readthedocs.io/en/stable/index.html)

## First step
We need to update the pre-commit file in the git hook folder of the repository. If the file does not exist, we should just create it.
```
{Repository}\.git\hooks\pre-commit
```

The file should contain the following command:
```
#!/bin/sh
python "{BaseFolder}\SonarCommit\main.py"
```

## Using
After adding the file at the stage and before the commit, the script executes SonarQube. If there is a problem, the error report opens automatically in the browser. The commit is only accepted if there are no problems encountered.
