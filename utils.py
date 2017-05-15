import sys
import http.client
import os
import shutil

def print_(text):
    """ Função para exibir texto e forçar atualização do console """

    print(text)
    sys.stdout.flush()

def verify_sonar_response(url):
    """ """

    print_(">> Verificando se SonarQube está em execução no servidor ...")

    try:
        url = url.replace("http://", "")
        sonarhttp = http.client.HTTPConnection(url)
        sonarhttp.request("HEAD", "/")
        response = sonarhttp.getresponse()
        print_("OK > SonarQube está em execução.")
    except Exception:
        print_("ERROR > SonarQube não está em execução. Análise abortada.")
        sys.exit(0)

def remove_file(file):
    """ Function to remove especific file """
    if os.path.isfile(file):
        os.remove(file)

def remove_folder(folder):
    """ Function to remove especific folder """

    if os.path.isdir(folder):
        shutil.rmtree(folder)

def find_systems_and_keys(repository):
    """ Function created for Mitsui.
    This function find systems and keys in ps1 file """

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
