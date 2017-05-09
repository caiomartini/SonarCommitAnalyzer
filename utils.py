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
        print_("   OK: SonarQube está em execução.")
    except Exception:
        print_("   ERROR: SonarQube não está em execução, a análise do código nao irá acontecer.")
        sys.exit(0)

def remove_file(file):
    """ """
    if os.path.isfile(file):
        os.remove(file)

def remove_folder(folder):
    """ """

    if os.path.isdir(folder):
        shutil.rmtree(folder)
