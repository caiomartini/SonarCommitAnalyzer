import subprocess
import urllib.request
import zipfile
import shutil
import os

print(">> Configuring First Run ...")

directory = "C:/Sonar"
os.makedirs(directory, exist_ok=True)

if not os.path.exists("C:/Sonar/sonar-scanner"):
    if not os.path.exists("C:/Sonar/sonar-scanner.zip"):
        print(">> Downloading Sonar Scanner ...")
        urllib.request.urlretrieve("https://sonarsource.bintray.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-3.0.3.778-windows.zip", "C:/Sonar/sonar-scanner.zip")    

if os.path.exists("C:/Sonar/sonar-scanner.zip"):
    with zipfile.ZipFile("C:/Sonar/sonar-scanner.zip", "r") as zipfile:
        zipfile.extractall("C:/Sonar")
    os.remove("C:/Sonar/sonar-scanner.zip")

if os.path.exists("C:/Sonar/sonar-scanner-3.0.3.778-windows"):
    os.rename("C:/Sonar/sonar-scanner-3.0.3.778-windows", "C:/Sonar/sonar-scanner")

directory = "C:/Sonar/issues-report"
os.makedirs(directory, exist_ok=True)

print("OK > Directories created.")

print(">> Instal GitPython ...")

output = subprocess.run("pip install GitPython", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, encoding="utf-8")

print(output.stdout)
