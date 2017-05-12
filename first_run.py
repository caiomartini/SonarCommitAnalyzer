import subprocess
import os

print(">> Configuring First Run ...")

directory = "C:/Sonar"
os.makedirs(directory, exist_ok=True)

directory = "C:/Sonar/issues-report"
os.makedirs(directory, exist_ok=True)

print("OK > Directories created.")

print(">> Instal GitPython ...")

output = subprocess.run("pip install GitPython", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, encoding="utf-8")

print(output.stdout)
