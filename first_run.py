import subprocess
import os

print(">> Configuring First Run ...")

directory = "C:/Sonar"
os.makedirs(directory, exist_ok=True)

directory = "C:/Sonar/issues-report"
os.makedirs(directory, exist_ok=True)

file = "C:/Sonar/template/template.sonarsource.properties"
os.makedirs(os.path.dirname(file), exist_ok=True)
if not os.path.isfile(file):
    with open(file, "w") as f:
        f.writelines("sonar.host.url={url}\n"\
                "sonar.login={login}\n"\
                "sonar.password={password}\n"\
                "\n"\
                "sonar.projectBaseDir={repository}\n"\
                "sonar.projectKey={key}\n"\
                "sonar.projectName={sistema}\n"\
                "sonar.projectVersion=1.0\n"\
                "\n"\
                "sonar.sources={path}\n"\
                "\n"\
                "sonar.analysis.mode=preview\n"\
                "\n"\
                "sonar.exclusions=**/*.js\n"\
                "\n"\
                "sonar.issuesReport.html.enable=true\n"\
                "sonar.issuesReport.html.location=C:/Sonar/issues-report/{sistema}/\n"\
                "sonar.issuesReport.html.name=issues-report-{sistema}\n"\
                "sonar.issuesReport.console.enable=true")

print("OK > Directories created.")

print(">> Instal GitPython ...")

output = subprocess.run("pip install GitPython", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, encoding="utf-8")

print(output.stdout)
