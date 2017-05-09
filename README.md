# SonarCommitAnalyzer ![logo](https://s3-ap-northeast-1.amazonaws.com/qiita-tag-image/acaa785eea912847ad246c30f4673f58f8748882/medium.jpg?1468193129)
Code analysis with SonarQube in pre-commit.

### Pre requirements
- Git
- Python 3.6.1
- SonarQube

### Python libraries
- [GitPython](https://gitpython.readthedocs.io/en/stable/index.html)

# Setting up
1. Clone this repo;
2. Install Python 3.6.1;
3. Install GitPython;
```
pip install GitPython
```
4. Create the necessary folders to run the SonarQube. These folders should follow the example below:
```
C:\
└ Sonar\
    ├ issues-report\
    ├ sonar-scanner\
    └ template\
        └ template.sonarsource.properties
```
_*Download sonar-scanner [here](https://docs.sonarqube.org/display/SCAN/Analyzing+with+SonarQube+Scanner)_

_*The template.sonarsource.properties file should contain the following content:_
```
sonar.host.url={url}
sonar.login={login}
sonar.password={password}

sonar.projectBaseDir={repository}
sonar.projectKey={key}
sonar.projectName={sistema}
sonar.projectVersion=1.0

sonar.sources={path}

sonar.analysis.mode=preview

sonar.exclusions=**/*.js

sonar.issuesReport.html.enable=true
sonar.issuesReport.html.location=C:/Sonar/issues_report/{sistema}/
sonar.issuesReport.html.name=issues-report-{sistema}
sonar.issuesReport.console.enable=true
```

5. Update the config.ini file to add the settings of your sonarqube server, repository, systems and on/off scan;
6. Update the commit_analyzer.py file to set config.ini path;
```
config = config_tool.ConfigTool("{SonarCommitAnalyzerRepository}/SonarCommitAnalyzer/config.ini")
```
7. Update the pre-commit file in the git hook folder of the repository. If the file does not exist, we should just create it.
```
{ProjectRepository}\.git\hooks\pre-commit
```

_*The file should contain the following content:_
```
#!/bin/sh
python "{SonarCommitAnalyzerRepository}\SonarCommitAnalyzer\main.py"
```
_*Update the {ProjectRepository} and {SonarCommitAnalyzerRepository} to your repository_
