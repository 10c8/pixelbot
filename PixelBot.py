#: vim set encoding=utf-8 :
##
 # Pixel Bot
 # Modular bot for Discord servers
 #
 # author William F.
 # version 0.4
 # copyright MIT
##

# Imports
import json
import logging
import re
import warnings
from ConfigManager import ConfigManager
from Client import Client


# Main class
class Bot(object):
    def __init__(self):
        self.client = None
        self.cfg = None
        self.cmd_regex = re.compile('(?P<command>\w+)\s*(?P<args>.*)?')
        self.settings = {}
        self.data = {}
        self.plugins = {}

        # Set up logging
        logging.basicConfig(filename='pixelbot.log',
                            format='[%(asctime)-15s] %(message)s',
                            level=logging.INFO)

        logging.info('Pixel Bot initialized.')

        # Load configuration
        logging.info('Loading configuration file.')
        self.cfg = ConfigManager('./config.ini')

        # Load settings
        logging.info('Loading settings.')
        print('Loading settings.')

        self.settings = {
            'discord': {
                'token': self.cfg.get('token', section='discord'),
                'mod_roles': self.cfg.get('mod_roles',
                                          section='discord').split(',')
            },
            'options': {
                'prefix': self.cfg.get('prefix', section='options')
            },
            'channels': {
                'welcome': self.cfg.get('welcome', section='channels'),
            }
        }

        # Load bot data
        logging.info('Loading data.')
        print('Loading data.')

        self.data = json.loads(open('./data.json').read())

    def start(self):
        # Initialize the Discord API
        self.client = Client(self)

        # Login into Discord
        logging.info('Logging in...')
        print('Logging in...')

        try:
            self.client.run(self.settings['discord']['token'])
        except Exception as e:
            logging.critical('Failed.')
            logging.critical(e)
            print('Logging in to Discord failed.')
            exit(1)

    def stop(self):
        self.client.logout()

    def install_plugins(self):
        to_load = dict(self.cfg.items('plugins', raw=True))

        for name in to_load:
            if to_load[name] != 'true':
                continue

            try:
                loc = {}
                exec(open('./plugins/{}.py'.format(name)).read(), loc, {})

                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    plugin = loc['__plugin__'](self)

                self.plugins[plugin.name.lower()] = plugin
            except Exception as e:
                logging.critical('Failed to load plugin "{}".'.format(name))
                logging.critical(e)
                print('Failed to load plugin "{}".'.format(name))
                exit(1)

    def saveData(self):
        logging.info('Data save requested, making a backup...')

        try:
            with open('data.json.bkp', 'w+') as bkp:
                bkp.write(open('data.json', 'r').read())
        except:
            logging.critical('Failed.')
            print('Failed to save data backup, aborting save.')
            exit(1)

        logging.info('Done.')
        logging.info('Saving data...')

        try:
            with open('data.json', 'w+') as data:
                data.write(json.dumps(self.data))

            logging.info('Done.')
        except:
            logging.critical('Error.')
            print('Error while saving data.')
            exit(1)


# Main code
if __name__ == '__main__':
    try:
        bot = Bot()
        bot.install_plugins()
        bot.start()
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt, disconnecting.")
        print('\nKeyboardInterrupt')
        bot.stop()
