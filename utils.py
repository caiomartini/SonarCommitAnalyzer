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

    print_(">> Verificando se SonarQube esta em execucao no servidor ...")

    try:
        sonarhttp = http.client.HTTPConnection(url)
        sonarhttp.request("HEAD", "/")
        response = sonarhttp.getresponse()
    except Exception:
        print_(">> SonarQube nao esta em execucao, a analise do codigo nao ira acontecer.")
        sys.exit(0)

def remove_file(file):
    """ """

    os.remove(file)

def remove_folder(folder):
    """ """

    if os.path.isdir(folder):
        shutil.rmtree(folder)
