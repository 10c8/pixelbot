#: vim set encoding=utf-8 :
##
 # PixelBot Plugin API
 # Tools for creating plugins for the bot
 #
 # version 0.2
 # author William F.
 # copyright MIT
##

# Imports
import asyncio
import logging


# Main class
class Plugin(object):
    def __init__(self, bot, name, description, version, author, data):
        self.bot = bot
        self.name = name
        self.desc = description
        self.version = version
        self.author = author
        self.data = {}
        self.default_data = data
        self.tasks = {}
        self.cmds = {}
        self.mod_cmds = {}

        # Fetch plugin data
        if not self.name in self.bot.data['plugins']:
            self.bot.data['plugins'][self.name] = self.default_data

        self.data = self.bot.data['plugins'][self.name]

        # Register tasks and commands
        logging.info('Registering plugin "{}".'.format(self.name))

        for method in dir(self):
            if callable(getattr(self, method)):
                call = getattr(self, method)

                if method.startswith('cmd_'):
                    call(None, None, None)
                elif method.startswith('task_'):
                    call(None)

    def init(plugin, bot):
        """Used to inherit from PluginAPI without calling the
           'bloated' super method"""

        default_data = {}

        if 'default_data' in plugin.__dir__():
            default_data = plugin.default_data

        super(type(plugin), plugin).__init__(bot,
                                             name=plugin.name,
                                             description=plugin.description,
                                             version=plugin.version,
                                             author=plugin.author,
                                             data=default_data)

    # Utils
    def saveData(self):
        self.bot.data['plugins'][self.name] = self.data
        self.bot.saveData()

    def getConfig(self, key):
        return self.bot.cfg.get(key, section=self.name)

    def log(self, message):
        logging.info('[INFO][{}] {}'.format(self.name, message))

    def warning(self, message):
        logging.critical('[WARN][{}] {}'.format(self.name, message))

    def critical(self, message):
        logging.critical('[FAIL][{}] {}'.format(self.name, message))

    def generateHelp(self, mod=False):
        info = (
            '**{name}**\n'
            '*{desc}*\n\n'
            'Version: {version}\n'
            'Commands:```{cmds}```'
        ).format(
            name=self.name,
            desc=self.description,
            version=self.version,
            cmds=self.generateHelp()
        )

        return info

    # Methods
    async def on_ready(self, client):
        pass

    async def on_message(self, client, msg):
        pass

    async def on_member_join(self, client, user):
        pass

    async def on_member_remove(self, client, user):
        pass

    async def on_member_update(self, client, before, after):
        pass


# User API
class _UserAPI(object):
    def __init__(self):
        pass

    def is_mod(self, plugin, user):
        """Returns True if the user is a mod (has any 'mod_roles' role)."""

        try:
            for role in user.roles:
                if role.name in plugin.bot.settings['discord']['mod_roles']:
                    return True
            return False
        except:
            return False

User = _UserAPI()


# Task class
class Task(object):
    def __init__(self, owner, name, func, interval, alive=True):
        self.owner = owner
        self.name = name
        self.func = func
        self.interval = interval
        self.alive = alive

    async def run(self, client):
        while self.alive:
            await self.func(self.owner, client)
            await asyncio.sleep(self.interval)

    def kill(self):
        logging.info('[{}] Task "{}" killed.'.format(self.owner.name,
                                                     self.name))
        self.alive = False

    def revive(self):
        logging.info('[{}] Task "{}" revived.'.format(self.owner.name,
                                                      self.name))
        self.alive = True
        self.owner.bot.client.loop.create_task(self.run(self.owner.bot.client))


# Task decorator
def task(name, interval, alive=True):
    """Make the function a bot task."""

    def wrapper(func):
        def wrapped(*args):
            this = Task(args[0], name, func, interval)
            this.alive = alive
            args[0].tasks[name] = this

            if args[1]:
                func(*args)
        return wrapped
    return wrapper


# Command decorator
def command(name, mod=False):
    def wrapper(func):
        def wrapped(*args):
            if mod:
                args[0].mod_cmds[name] = func
            else:
                args[0].cmds[name] = func

            if args[1]:
                func(*args)
        return wrapped
    return wrapper
