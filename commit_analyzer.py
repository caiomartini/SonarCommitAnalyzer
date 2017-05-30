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

        self.git_repository = git.Repo(self.base_repository)
        self.git_command = git.Git(self.base_repository)
        self.systems_and_keys = utils.find_systems_and_keys(self.base_ci)

        self.modules = config.configsectionmap("Modules")

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
            utils.error_text("Não foi possível encontrar os sistemas a partir dos arquivos modificados.")
            utils.system_exit_ok()

    def find_modified_systems(self, file):
        """ Function to find systems. """
        try:
            file = file.a_path
            system = list({system["System"] for system in self.systems_and_keys if system["Solution_Path"].replace("\\", "/") in file})[0]
            file_dictionary = {"System": system, "File": file}
            return file_dictionary

        except Exception:
            utils.error_text("Não foi possível encontrar os sistemas a partir dos arquivos modificados.")
            utils.system_exit_ok()

    def find_modified_files(self):
        """ Function to find modified files. """
        utils.print_(">> Analisando arquivos C# no stage ...")        

        try:
            modified_files = self.git_repository.head.commit.diff()

            if not modified_files:
                utils.ok_text("Nenhum arquivo alterado.")
                utils.system_exit_ok()            

            for file in modified_files:
                _, file_extension = os.path.splitext(file.a_path)
                if file.change_type != "D" and file_extension.lower() == ".cs":
                    dictionary = self.find_modified_systems(file)
                    self.files.append(dictionary)            

            if len(self.files) == 0:
                utils.ok_text("Nenhum arquivo alterado.")
                utils.system_exit_ok()

            utils.print_("Arquivos alterados:")
            self.systems = {file["System"] for file in self.files}
            self.systems = sorted(self.systems)            

            for system in self.systems:
                index = list(self.systems).index(system)+1
                utils.print_("{}. {}".format(index, system))
                files = {file["File"] for file in self.files if file["System"] == system}
                files = sorted(files)
                for file in files:
                    utils.print_(" - " + file)
                    # To show characters ├ and └ (not working in pearl)
                    #if list(files).index(file) == len(files)-1:
                    #    utils.print_(u"       \u2514 " + file)
                    #else:
                    #    utils.print_(u"       \u251c " + file)
            utils.print_("")

        except Exception:
            utils.error_text("Não foi possível encontrar os arquivos modificados no stage.")
            utils.system_exit_ok()

    def remove_configuration_file(self, system):
        """ Function to remove sonar configuration file. """
        utils.print_(">> Removendo arquivo de configuração ...")        

        try:
            utils.remove_file(self.sonar_folder + "{}.sonarsource.properties".format(system))
            utils.ok_text("Arquivo {}.sonarsource.properties removido com sucesso.".format(system))

        except Exception:
            utils.error_text("Não foi possível remover o arquivo de configuração do sistema {}".format(system))
            utils.system_exit_ok()

    def run_sonar(self, system):
        """ Function to run sonar-scanner. """
        utils.print_(">> Executando SonarQube no sistema {} ...".format(system))        

        try:
            command = self.sonar_scanner + " -D project.settings={}{}.sonarsource.properties".format(self.sonar_folder, system)
            output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, encoding="utf-8")

            if "EXECUTION FAILURE" in output.stdout:
                utils.error_text("Não foi possível executar o SonarQube no sistema {}".format(system))
                utils.system_exit_ok()

            if "major" in output.stdout or "critical" in output.stdout:
                webbrowser.open(self.sonar_folder + "issues-report/{}/issues-report-{}.html".format(system, system), new=2)
                utils.ok_text("Relatório disponibilizado no navegador.")
                self.scanner_error = True
            else:
                utils.ok_text("Análise concluída.")

        except Exception:
            utils.error_text("Não foi possível executar o SonarQube no sistema {}".format(system))
            utils.system_exit_ok()

        self.remove_configuration_file(system)

    def preparing_sonar(self, system):
        """ Function to preparing sonar-scanner execution. """
        utils.print_(">> Preparando execução do SonarQube no sistema {} ...".format(system))        

        replacements = {
            "{url}": self.sonar_server,
            "{login}": self.sonar_login,
            "{password}": self.sonar_password,
            "{repository}": self.base_repository,
            "{key}": list({item["Key"] for item in self.systems_and_keys if item["System"] == system})[0],
            "{branch}": self.git_repository.active_branch.name,
            "{files}": ",".join({file["File"] for file in self.files if file["System"] == system}),
            "{language}": list({item["Language"] for item in self.systems_and_keys if item["System"] == system})[0],
            "{system}": system         
        }
                
        replacements.update({"{modules}": utils.write_modules(self.modules.items(), self.files, system)})
        
        lines = []
        with open(self.sonar_template) as infile:
            for line in infile:
                for src, target in replacements.items():
                    line = line.replace(src, target)
                lines.append(line)

        with open(self.sonar_folder + "{}.sonarsource.properties".format(system), 'w') as outfile:
            for line in lines:
                outfile.write(line)

        utils.ok_text("Arquivo {}.sonarsource.properties criado com sucesso.".format(system))

    def commit_analyzer(self):
        """ Main function to analyze commit. """

        utils.verify_branch_merging(self.git_command)

        if self.scan_status:
            utils.print_("\n>-------------------------------------------<")
            utils.print_("> ANÁLISE DE CÓDIGO PELO SONARQUBE INICIADO <")
            utils.print_(">-------------------------------------------<\n")

            self.find_modified_files()

            utils.verify_sonar_response(self.sonar_server)

            for system in self.systems:
                self.preparing_sonar(system)
                self.run_sonar(system)

            utils.remove_folder("{}.scannerwork".format(self.base_repository))
            utils.print_(">> Análise de qualidade de código pelo SonarQube finalizada.")

            if self.scanner_error:
                utils.warning_text("Existem problemas críticos de qualidade, verifique o relatório no navegador. Commit recusado.")
                utils.system_exit_block_commit()
            else:
                utils.ok_text("Nenhum problema encontrado. Commit liberado.")
                utils.system_exit_ok()
        else:
            utils.warning_text(">> Análise de qualidade de código pelo SonarQube está desativada.")
            utils.system_exit_ok()
