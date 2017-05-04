import os
import subprocess
import sys
import webbrowser
import git
import config_tool
import utils

class CommitAnalyzer(object):
    """ """

    def __init__(self):
        config = config_tool.ConfigTool("C:\\Users\\Caio\\Desktop\\SonarCommit\\config.ini")
        repositoryconfig = config.configsectionmap("Repository")
        sonarconfigs = config.configsectionmap("Sonar")
        self.sonar_scanner = sonarconfigs["scanner"]
        self.sonar_server = sonarconfigs["url"]
        self.sonar_folder = sonarconfigs["basefolder"]
        self.template = sonarconfigs["template"]
        self.base_repository = repositoryconfig["repository"]
        self.files = []
        self.systems = []
        self.scanner_error = False

    def find_systems(self, file):
        """ Função para buscar sistemas alterados a partir dos arquivos do stage """

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

    def find_modified_files(self):
        """ """

        utils.print_(">> Analisando arquivos no stage ...")

        repository = git.Repo(self.base_repository)
        modified_files = repository.head.commit.diff()
        if not modified_files:
            utils.print_(">> Nenhum arquivo foi alterado.")
            sys.exit(0)
        for file in modified_files:
            if file.change_type != "D":
                dictionary = self.find_systems(file)
                self.files.append(dictionary)
        utils.print_(">> Arquivos alterados:")
        self.systems = {file["System"] for file in self.files}
        for system in self.systems:
            index = list(self.systems).index(system)+1
            utils.print_("    {}.{}".format(index, system.upper()))
            files = {file["File"] for file in self.files if file["System"] == system}
            for file in files:
                utils.print_("     |- " + file)
    def remove_configuration_file(self, system):
        """ """

        utils.print_(">> Removendo arquivo de configuração do sistema {} ...".format(system))

        utils.remove_file(self.sonar_folder + r"\{}.sonarsource.properties".format(system))

    def run_sonar(self, system):
        """ """

        utils.print_(">> Executando SonarQube no sistema {} ...".format(system))

        command = self.sonar_scanner + " -e " \
            + " -Dsonar.host.url=http:\\" + self.sonar_server \
            + " -Dsonar.projectBaseDir=" + self.base_repository \
            + " -Dproject.settings=" + self.sonar_folder + r"\{}.sonarsource.properties".format(system)
        output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, encoding="utf-8")

        self.remove_configuration_file(system)

        if "major" in output.stdout or "critical" in output.stdout:
            webbrowser.open(self.sonar_folder + r"\issues_report\{}\issues-report-{}.html".format(system, system), new=2)
            self.scanner_error = True

    def preparing_sonar(self, system):
        """ """

        utils.print_(">> Preparando execução do SonarQube no sistema {} ...".format(system))

        files = {file["File"] for file in self.files if file["System"] == system}
        replacements = {"{sistema}": system, "{path}": ",".join(files)}
        lines = []
        with open(self.template) as infile:
            for line in infile:
                for src, target in replacements.items():
                    line = line.replace(src, target)
                lines.append(line)
        with open(self.sonar_folder + r"\{}.sonarsource.properties".format(system), 'w') as outfile:
            for line in lines:
                outfile.write(line)

    def commit_analyzer(self):
        """ """

        utils.print_("\n")
        utils.print_(">> Processo de análise de código pelo SonarQube iniciado.")

        self.find_modified_files()
        utils.verify_sonar_response(self.sonar_server)
        for system in self.systems:
            self.preparing_sonar(system)
            self.run_sonar(system)
        utils.remove_folder("{}/.scannerwork".format(self.base_repository))
        if self.scanner_error:
            utils.print_(">> Foram encontrados problemas críticos de qualidade.")
            utils.print_(">> Verifique o relatório aberto no browser e faca as correções antes de efetuar o commit.")
            sys.exit(1)
        utils.print_(">> Análise de qualidade de código pelo SonarQube finalizada. Nenhum problema foi encontrado. Commit liberado.")
