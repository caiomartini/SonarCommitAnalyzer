# SonarCommitAnalyzer ![logo](https://s3-ap-northeast-1.amazonaws.com/qiita-tag-image/acaa785eea912847ad246c30f4673f58f8748882/medium.jpg?1468193129)
Code analysis with SonarQube in pre-commit.

### Pre requirements
- Git
- Python 3.6.1
- SonarQube

### Python libraries
- [GitPython](https://gitpython.readthedocs.io/en/stable/index.html)

# Setting up
1. Install Python 3.6.1;
2. Clone this repository;
3. Execute `python first_run.py` in cmd prompt;
4. Download sonar-scanner [here](https://docs.sonarqube.org/display/SCAN/Analyzing+with+SonarQube+Scanner), rename to `sonar-scanner` and move it to the previously created `Sonar` folder.
```
C:\Sonar\
├ issues-report\
├ sonar-scanner\
```
5. Update the `config.ini` to add the settings of your sonarqube server, repository, systems and on/off scan;
6. Update or create pre-commit file in the git hook folder of the repository `{your_repository}\.git\hooks\pre-commit`. The file should contain the following content:
```
#!/bin/sh
python "{replace}\SonarCommitAnalyzer\main.py"
```
