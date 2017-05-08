import os
import subprocess
import sys
import webbrowser
import git
import config_tool
import utils

class CommitAnalyzer(object):
    """ Class to analyze commit. """

    def __init__(self):
        config = config_tool.ConfigTool("C:/Users/Caio/Desktop/SonarCommitAnalyzer/config.ini")

        sonarconfigs = config.configsectionmap("Sonar")
        self.sonar_scanner = sonarconfigs["scanner"]
        self.sonar_server = sonarconfigs["url"]
        self.sonar_folder = sonarconfigs["basefolder"]
        self.template = sonarconfigs["template"]

        repositoryconfig = config.configsectionmap("Repository")
        self.base_repository = repositoryconfig["repository"]

        self.keyconfig = config.configsectionmap("SystemKey")

        self.files = []
        self.systems = []
        self.scanner_error = False

    def find_systems(self, file):
        """ Function to find systems. """

        try:
            file = file.a_path

            file_folders = file.split("/")

            folder = self.base_repository + "/" + file.replace("/" + file_folders[len(file_folders)-1], "")

            for i in range(len(file_folders)-1, 0, -1):
                folder = folder.replace("/" + file_folders[i], "")

                for _, _, files in os.walk(folder):
                    for file_system in files:
                        if file_system.endswith(".sln"):
                            file_dictionary = {"System": file_system.replace(".sln", ""), "File": file}
                            return file_dictionary
        except Exception:
            utils.print_("ERRO: Não foi possível encontrar os sistemas a partir dos arquivos modificados.")
            sys.exit(0)

    def find_modified_files(self):
        """ Function to find modified files. """

        utils.print_(">> Analisando arquivos no stage ...")

        try:
            repository = git.Repo(self.base_repository)

            modified_files = repository.head.commit.diff()

            if not modified_files:
                utils.print_("   Nenhum arquivo foi alterado.")
                sys.exit(0)

            for file in modified_files:
                if file.change_type != "D":
                    dictionary = self.find_systems(file)
                    self.files.append(dictionary)

            utils.print_("   Arquivos alterados:")

            self.systems = {file["System"] for file in self.files}

            for system in self.systems:
                index = list(self.systems).index(system)+1
                utils.print_("   {}. {}".format(index, system.upper()))
                files = {file["File"] for file in self.files if file["System"] == system}
                for file in files:
                    if list(files).index(file) == len(files)-1:
                        utils.print_(u"       \u2514 " + file)
                    else:
                        utils.print_(u"       \u251c " + file)
        except Exception:
            utils.print_("ERRO: Não foi possível encontrar os arquivos modificados no stage.")

    def remove_configuration_file(self, system):
        """ Function to remove sonar configuration file. """

        utils.print_(">> Removendo arquivo de configuração do sistema {} ...".format(system.upper()))

        try:
            utils.remove_file(self.sonar_folder + "/{}.sonarsource.properties".format(system))
            utils.print_("   OK")
        except Exception:
            utils.print_("ERRO: Não foi possível remover o arquivo de configuração do sistema {}".format(system.upper()))

    def run_sonar(self, system):
        """ Function to run sonar-scanner. """

        utils.print_(">> Executando SonarQube no sistema {} ...".format(system.upper()))

        try:
            command = self.sonar_scanner + " -D project.settings={}/{}.sonarsource.properties".format(self.sonar_folder, system)

            output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, encoding="utf-8")

            if "major" in output.stdout or "critical" in output.stdout:
                webbrowser.open(self.sonar_folder + "/issues_report/{}/issues-report-{}.html".format(system, system), new=2)
                utils.print_("   Relatório de problemas do sistema {} disponibilizado.".format(system.upper()))
                self.scanner_error = True
            else:
                utils.print_("   OK")
        except Exception:
            utils.print_("ERRO: Não foi possível executar o SonarQube no sistema {}".format(system.upper()))

        self.remove_configuration_file(system)

    def preparing_sonar(self, system):
        """ Function to preparing sonar-scanner execution. """

        utils.print_(">> Preparando execução do SonarQube no sistema {} ...".format(system.upper()))

        files = {file["File"] for file in self.files if file["System"] == system}

        replacements = {
            "{url}": self.sonar_server,
            "{repository}": self.base_repository,
            "{key}": self.keyconfig[system.lower()],
            "{sistema}": system,
            "{path}": ",".join(files)
        }

        lines = []

        with open(self.template) as infile:
            for line in infile:
                for src, target in replacements.items():
                    line = line.replace(src, target)
                lines.append(line)

        with open(self.sonar_folder + "/{}.sonarsource.properties".format(system), 'w') as outfile:
            for line in lines:
                outfile.write(line)

        utils.print_("   OK")

    def commit_analyzer(self):
        """ Main function to analyze commit. """

        utils.print_("\n")
        utils.print_(">> Processo de análise de código pelo SonarQube iniciado.")

        self.find_modified_files()

        utils.verify_sonar_response(self.sonar_server)

        for system in self.systems:
            self.preparing_sonar(system)
            self.run_sonar(system)

        utils.remove_folder("{}/.scannerwork".format(self.base_repository))

        utils.print_(">> Análise de qualidade de código pelo SonarQube finalizada.")

        if self.scanner_error:
            utils.print_("   Foram encontrados problemas críticos de qualidade.")
            utils.print_("   Verifique o relatório aberto no navegador e faça as correções antes de efetuar o commit.")
            sys.exit(1)
        
        utils.print_("   Nenhum problema foi encontrado. Commit liberado.")
