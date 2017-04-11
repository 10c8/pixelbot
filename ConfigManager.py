#: vim set encoding=utf-8 :
##
 # file: ConfigManager.py
 # Just a configparser handler
 #
 # version 0.1
 # author William F.
 # copyright MIT
##

# Imports
import json
import configparser


# Main class
class ConfigManager(object):
    def __init__(self, cfg_file):
        self.parser = configparser.ConfigParser()
        self.parser.read(cfg_file)

    def get_json(self, key, section='settings', default=None):
        value = self.get(key, section=section)

        if value is None:
            return default

        return json.loads(value)

    def get(self, key, section='settings', default=None):
        try:
            value = self.parser.get(section, key)
        except configparser.NoSectionError:
            msg = ('WARN: Section {} not found in the settings. Value for '
                   '{} set to {}.').format(section, key, default)
            print(msg)
        except configparser.NoOptionError:
            msg = ('WARN: Option {} not found in the settings. '
                   'Set to {}.').format(key, default)
            print(msg)
        except:
            raise
        else:
            return value

        return default

    def items(self, section='settings', raw=False, vars=None):
        return self.parser.items(section, raw, vars)
