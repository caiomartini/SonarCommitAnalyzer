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
        config = config_tool.ConfigTool("{replace}/SonarCommitAnalyzer/config.ini")
        sonarconfigs = config.configsectionmap("Sonar")
        self.sonar_scanner = sonarconfigs["scanner"]
        self.sonar_server = sonarconfigs["url"]
        self.sonar_login = sonarconfigs["login"]
        self.sonar_password = sonarconfigs["password"]
        self.sonar_folder = sonarconfigs["folder"]
        self.sonar_template = sonarconfigs["template"]
        repositoryconfig = config.configsectionmap("Repository")
        self.base_repository = repositoryconfig["repository"]
        self.base_ci = repositoryconfig["ci"]
        scanstatus = config.configsectionmap("Status")
        self.scan_status = scanstatus["on"].lower() == "true"
        self.systems_and_keys = utils.find_systems_and_keys(self.base_ci)
        self.files = []
        self.systems = []
        self.scanner_error = False

    def find_modifed_systems_in_file_folders(self, file):
        """ Function to find systems in file folders. """
        try:
            file = file.a_path
            file_folders = file.split("/")
            folder = self.base_repository + file.replace("/" + file_folders[len(file_folders)-1], "")
            for i in range(len(file_folders)-1, 0, -1):
                folder = folder.replace("/" + file_folders[i], "")
                for _, _, files in os.walk(folder):
                    for file_system in files:
                        if file_system.endswith(".sln"):
                            file_dictionary = {"System": file_system.replace(".sln", ""), "File": file}
                            return file_dictionary
        except Exception:
            utils.print_("ERRO > Não foi possível encontrar os sistemas a partir dos arquivos modificados.")
            sys.exit(0)

    def find_modified_systems(self, file):
        """ Function to find systems. """
        try:
            file = file.a_path
            system = list({system["System"] for system in self.systems_and_keys if system["Solution_Path"] in file})[0]
            file_dictionary = {"System": system, "File": file}
            return file_dictionary
        except Exception:
            utils.print_("ERRO > Não foi possível encontrar os sistemas a partir dos arquivos modificados.")
            sys.exit(0)

    def find_modified_files(self):
        """ Function to find modified files. """
        utils.print_(">> Analisando arquivos no stage ...")
        
        try:
            repository = git.Repo(self.base_repository)
            modified_files = repository.head.commit.diff()
            
            if not modified_files:
                utils.print_("OK > Nenhum arquivo foi alterado.")
                sys.exit(0)
            
            for file in modified_files:
                _, file_extension = os.path.splitext(file.a_path)
                if file.change_type != "D" and file_extension == ".cs":
                    dictionary = self.find_modified_systems(file)
                    self.files.append(dictionary)
            
            if len(self.files) == 0:
                utils.print_("OK > Nenhum arquivo C# foi alterado.")
                sys.exit(0)
            utils.print_("Arquivos C# alterados:")
            self.systems = {file["System"] for file in self.files}
            self.systems = sorted(self.systems)
            
            for system in self.systems:
                index = list(self.systems).index(system)+1
                utils.print_("{}. {}".format(index, system))
                files = {file["File"] for file in self.files if file["System"] == system}
                files = sorted(files)
                for file in files:
                    utils.print_(" - " + file)
                    # To show characters ├ and └
                    #if list(files).index(file) == len(files)-1:
                    #    utils.print_(u"       \u2514 " + file)
                    #else:
                    #    utils.print_(u"       \u251c " + file)
        except Exception:
            utils.print_("ERRO > Não foi possível encontrar os arquivos modificados no stage.")
            sys.exit(0)

    def remove_configuration_file(self, system):
        """ Function to remove sonar configuration file. """
        utils.print_(">> Removendo arquivo de configuração ...")
        
        try:
            utils.remove_file(self.sonar_folder + "{}.sonarsource.properties".format(system))
            utils.print_("OK > Arquivo de configuração {}.sonarsource.properties removido com sucesso.".format(system))
        except Exception:
            utils.print_("ERRO > Não foi possível remover o arquivo de configuração do sistema {}".format(system))
            sys.exit(0)

    def run_sonar(self, system):
        """ Function to run sonar-scanner. """
        utils.print_(">> Executando SonarQube no sistema {} ...".format(system))
        
        try:
            command = self.sonar_scanner + " -D project.settings={}{}.sonarsource.properties".format(self.sonar_folder, system)
            output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, encoding="utf-8")
            if "EXECUTION FAILURE" in output.stdout:
                utils.print_("ERRO > Não foi possível executar o SonarQube no sistema {}".format(system))
                sys.exit(0)
            if "major" in output.stdout or "critical" in output.stdout:
                webbrowser.open(self.sonar_folder + "issues-report/{}/issues-report-{}.html".format(system, system), new=2)
                utils.print_("OK > Relatório disponibilizado no navegador.")
                self.scanner_error = True
            else:
                utils.print_("OK > Não foi encontrado nenhum problema no sistema {}".format(system))
        except Exception:
            utils.print_("ERRO > Não foi possível executar o SonarQube no sistema {}".format(system))
            sys.exit(0)

        self.remove_configuration_file(system)

    def preparing_sonar(self, system):
        """ Function to preparing sonar-scanner execution. """
        utils.print_(">> Preparando execução do SonarQube no sistema {} ...".format(system))
        
        lines = []
        replacements = {
            "{url}": self.sonar_server,
            "{login}": self.sonar_login,
            "{password}": self.sonar_password,
            "{repository}": self.base_repository,
            "{key}": list({item["Key"] for item in self.systems_and_keys if item["System"] == system})[0],
            "{system}": system,
            "{version}": list({item["Version"] for item in self.systems_and_keys if item["System"] == system})[0],
            "{path}": ",".join({file["File"] for file in self.files if file["System"] == system}),
            "{language}": list({item["Language"] for item in self.systems_and_keys if item["System"] == system})[0]
        }

        with open(self.sonar_template) as infile:
            for line in infile:
                for src, target in replacements.items():
                    line = line.replace(src, target)
                lines.append(line)

        with open(self.sonar_folder + "{}.sonarsource.properties".format(system), 'w') as outfile:
            for line in lines:
                outfile.write(line)

        utils.print_("OK > Arquivo de configuração {}.sonarsource.properties criado com sucesso.".format(system))

    def commit_analyzer(self):
        """ Main function to analyze commit. """
        utils.print_("\n")
        utils.print_(">> Processo de análise de código pelo SonarQube iniciado.")
        
        self.find_modified_files()
        if self.scan_status:
            utils.verify_sonar_response(self.sonar_server)
            for system in self.systems:
                self.preparing_sonar(system)
                self.run_sonar(system)
            utils.remove_folder("{}.scannerwork".format(self.base_repository))
            utils.print_(">> Análise de qualidade de código pelo SonarQube finalizada.")
            if self.scanner_error:
                utils.print_("WARN > Foram encontrados problemas críticos de qualidade, verifique o relatório no navegador.")
                utils.print_("WARN > Commit recusado.")
                sys.exit(1)
            utils.print_("OK > Nenhum problema foi encontrado. Commit liberado.")
        else:
            utils.print_(">> Análise de qualidade de código pelo SonarQube desativada.")
