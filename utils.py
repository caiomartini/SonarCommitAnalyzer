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
    print_(">> Verificando se SonarQube esta em execucao no servidor ...")

    try:
        http_url = url.replace("http://", "")
        sonarhttp = http.client.HTTPConnection(http_url)
        sonarhttp.request("HEAD", "/")
        response = sonarhttp.getresponse()
        ok_text("SonarQube em execucao no servidor {}.".format(url))

    except Exception:
        error_text("SonarQube nao esta em execucao. Commit liberado.")
        system_exit_ok()

def remove_file(file):
    """ Function to remove especific file. """
    if os.path.isfile(file):
        os.remove(file)

def remove_folder(folder):
    """ Function to remove especific folder. """
    if os.path.isdir(folder):
        shutil.rmtree(folder)

def verify_branch_is_merging(git_command):
    """ Function to verify branch is merging. """
    branch_merging = git_command.execute("git status")

    if "All conflicts fixed but you are still merging." in branch_merging:
        ok_text(">> Commit de MERGE. SonarQube nao sera executado.")
        system_exit_ok()

def find_systems_and_keys(repository):
    """ Function find systems and keys in ps1 file. """
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
        error_text("Nao foi possível encontrar os sistemas no arquivo Configuracoes.ps1.")
        system_exit_ok()

def write_modules(modules_list, files, system):
    try:
        modules = []
        modules_string = ""
        if "MS10Plus" in system or "MS10Plus_Malha" in system:
            if len(modules_list) > 0:
                modules_list = sorted(modules_list)
                for module in modules_list:
                    module_files = ",".join({file["File"].replace(module[1] + "/", "") for file in files if file["System"] == system and module[1] in os.path.dirname(file["File"])})
                    if module_files != "":
                        module_title = "WebServices" if "webservices" in module[0] else module[0].title()
                        module_dict = {
                            "Module": module_title,
                            "BaseDir": "{}.sonar.projectBaseDir={}".format(module_title, module[1]),
                            "Files": "{}.sonar.inclusions={}".format(module_title, module_files)
                        }
                        modules.append(module_dict)
                modules_string = "sonar.modules=" + ",".join(sorted({module["Module"] for module in modules})) + "\n"
                for module in modules:
                    modules_string += "\n"
                    modules_string += module["BaseDir"] + "\n"
                    modules_string += module["Files"] + "\n"            
        return modules_string
    except Exception as err:
        error_text("Nao foi possivel gerar os modulos do SonarQube.")
        system_exit_ok()

def system_exit_block_commit():
    sys.exit(1)

def system_exit_ok():
    sys.exit(0)

def warning_text(text):
    print_("\033[93mWARNING - {}\033[0m\n".format(text))

def ok_text(text):
    print_("\033[92mOK - {}\033[0m\n".format(text))

def error_text(text):
    print_("\033[91mERROR - {}\033[0m\n".format(text))