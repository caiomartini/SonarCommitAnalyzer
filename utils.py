import sys
import http.client
import os
import shutil

def print_(text):
    """ Function to print and flush console. """
    print(text)
    sys.stdout.flush()

def verify_sonar_response(url):
    """ Function to verify SonarQube is running on server. """
    print_(">> Verificando se SonarQube está em execução no servidor ...")

    try:
        http_url = url.replace("http://", "")
        sonarhttp = http.client.HTTPConnection(http_url)
        sonarhttp.request("HEAD", "/")
        response = sonarhttp.getresponse()
        ok_text("SonarQube em execução no servidor {}.".format(url))

    except Exception:
        error_text("SonarQube não está em execução. Commit liberado.")
        system_exit_ok()

def remove_file(file):
    """ Function to remove especific file. """
    if os.path.isfile(file):
        os.remove(file)

def remove_folder(folder):
    """ Function to remove especific folder. """
    if os.path.isdir(folder):
        shutil.rmtree(folder)

def verify_branch_merging(git_command):
    """ Function to verify branch is merging. """
    branch_merging = git_command.execute("git status")

    if "All conflicts fixed but you are still merging." in branch_merging:
        ok_text(">> Commit de MERGE. SonarQube não será executado.")
        system_exit_ok()

def find_systems_and_keys(repository):
    """ Created for Mitsui. Function find systems and keys in ps1 file. """
    try:
        file = repository + "Configuracoes.ps1"

        replacements = {
            "),\n": "",
            ")\n": ""
        }

        systems_keys = []

        with open(file, encoding="utf8") as f:
            for line in f:
                if "new-DotNetSolution -ID" in line:
                    find_line = list(line.replace("'", "").split(" "))

                    solution = find_line[find_line.index("-Solution") + 1].split("\\")
                    key = find_line[find_line.index("-ID") + 1]
                    solution_path = find_line[find_line.index("-Solution") + 1].replace(solution[len(solution)-1], "")
                    solution = list({index for index in find_line[find_line.index("-Solution") + 1].split("\\") if ".sln" in index})[0].replace(".sln", "")
                    version = find_line[find_line.index("-Version") + 1]
                    language = find_line[find_line.index("-Language") + 1]

                    for src, target in replacements.items():
                        key = key.replace(src, target)
                        solution = solution.replace(src, target)
                        version = version.replace(src, target)
                        language = language.replace(src, target)

                    system = {
                        "System": solution,
                        "Key": key,
                        "Solution_Path": solution_path,
                        "Version": version,
                        "Language": language
                    }

                    systems_keys.append(system)

        return systems_keys
    except Exception:
        error_text("Não foi possível encontrar os sistemas no arquivo Configuracoes.ps1.")
        system_exit_ok()

def system_exit_block_commit():
    sys.exit(1)

def system_exit_ok():
    sys.exit(0)

def warning_text(text):
    print_("\033[93mWARN - {}\033[0m\n".format(text));

def ok_text(text):
    print_("\033[92mOK - {}\033[0m\n".format(text));

def error_text(text):
    print_("\033[91mERROR - {}\033[0m\n".format(text));