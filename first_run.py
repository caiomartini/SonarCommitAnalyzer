import subprocess
import urllib.request
import zipfile
import shutil
import os

url_sonar_scanner = "https://sonarsource.bintray.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-3.0.3.778-windows.zip"
sonar_scanner_zip = "C:/Sonar/sonar-scanner.zip"

print(">> Configuring First Run ...")

directory = "C:/Sonar"
os.makedirs(directory, exist_ok=True)
if not os.path.exists("C:/Sonar/sonar-scanner"):
    if not os.path.exists(sonar_scanner_zip):
        print(">> Downloading Sonar Scanner ...")
        urllib.request.urlretrieve(url_sonar_scanner, sonar_scanner_zip)    

if os.path.exists(sonar_scanner_zip):
    with zipfile.ZipFile(sonar_scanner_zip, "r") as zipfile:
        zipfile.extractall("C:/Sonar")
    os.remove(sonar_scanner_zip)

if os.path.exists("C:/Sonar/sonar-scanner-3.0.3.778-windows"):
    os.rename("C:/Sonar/sonar-scanner-3.0.3.778-windows", "C:/Sonar/sonar-scanner")

directory = "C:/Sonar/issues-report"
os.makedirs(directory, exist_ok=True)

print("OK > Directories created.")

print(">> Instal GitPython ...")

output = subprocess.run("pip install GitPython", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, encoding="utf-8")

print(output.stdout)
