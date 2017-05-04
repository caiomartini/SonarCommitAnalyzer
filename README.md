# SonarCommitAnalyzer ![logo](https://s3-ap-northeast-1.amazonaws.com/qiita-tag-image/acaa785eea912847ad246c30f4673f58f8748882/medium.jpg?1468193129)
Code analysis with SonarQube in pre-commit.

### Pre requirements
- Git
- Python 3.6.1
- SonarQube

### Python libraries pre requirements
- [GitPython](https://gitpython.readthedocs.io/en/stable/index.html)

# First steps
1. We need to create the necessary folders to run the SonarQube. These folders should follow the example below:
```
C:\
└ Sonar\
    ├ issues-report\
    ├ sonar-scanner\
    └ template\
        └ template.sonarsource.properties
```
## Attention
**_Download the [sonar-scanner](https://docs.sonarqube.org/display/SCAN/Analyzing+with+SonarQube+Scanner)_**

**_The template.sonarsource.properties file should contain the following content:_**
```
sonar.projectKey={sistema}
sonar.projectName={sistema}
sonar.sources={path}
sonar.projectVersion=1.0

sonar.issuesReport.html.enable=true
sonar.issuesReport.html.location=C:/Sonar/issues_report/{sistema}/
sonar.issuesReport.html.name=issues-report-{sistema}
sonar.issuesReport.lightModeOnly

sonar.issuesReport.console.enable=true
sonar.analysis.mode=preview
```

2. We need to update the pre-commit file in the git hook folder of the repository. If the file does not exist, we should just create it.
```
{Repository}\.git\hooks\pre-commit
```

The file should contain the following command:
```
#!/bin/sh
python "{BaseFolder}\SonarCommitAnalyzer\main.py"
```

# Using
After adding the file at the stage and before the commit, the script executes SonarQube. If there is a problem, the error report opens automatically in the browser. The commit is only accepted if there are no problems encountered.
