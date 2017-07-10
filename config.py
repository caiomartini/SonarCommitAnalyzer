import sys
from configparser import ConfigParser

class ConfigTool(object):
    """ This object realises the parser and index of the configuration files """

    def __init__(self, config_path):
        self.config = ConfigParser()
        self.config.read(config_path)

    def configsectionmap(self, section):
        """ Realises the parse of a configuration section.
        Keyword arguments:
        section -- the named section on the configuration file (ie: [ConfigSection])
        """
        dict1 = {}
        options = self.config.options(section)
        for option in options:
            try:
                dict1[option] = self.config.get(section, option)
            except Exception:
                print("exception on %s!" % sys.exc_info()[0])
                dict1[option] = None
        return dict1
        