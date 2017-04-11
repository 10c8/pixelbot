#: vim set encoding=utf-8 :
##
 # file: Client.py
 # The bridge between Discord and bot plugins
 #
 # version 0.2
 # author William F.
 # copyright MIT
##

# Imports
import discord
import logging
import os.path
import os
import subprocess


# Main class
class Client(discord.Client):
    def __init__(self, bot):
        super(Client, self).__init__()

        self.bot = bot

    async def on_ready(self):
        print('Bot connected. ({})'.format(self.user.id))
        logging.info('Connected to Discord server as {}#{}.'
                     .format(self.user.name, self.user.id))

        # Run plugins "on_ready" functions
        for plugin in self.bot.plugins.values():
            await plugin.on_ready(self)

        # Register tasks
        logging.info('Registering plugin tasks...')
        print('Registering plugin tasks...')

        for plugin in self.bot.plugins.values():
            for task in plugin.tasks.values():
                logging.info('{}:'.format(task.name))

                try:
                    self.loop.create_task(task.run(self))
                    logging.info('Ok.')
                except Exception as e:
                    logging.critical('Failed.')
                    logging.critical(e)
                    print('Error registering plugin task "{}".'
                          .format(task.name))
                    exit(1)

        logging.info('Done.')
        print('Done.')

    async def on_message(self, msg):
        # Run plugins "on_message" functions
        for plugin in self.bot.plugins.values():
            await plugin.on_message(self, msg)

        # Parse the message
        if msg.content[0] == self.bot.settings['options']['prefix']:
            if not msg.channel.is_private:
                logging.info('#{} ({} #{}): {}'.format(msg.channel.name,
                                                       msg.author.name,
                                                       msg.author.id,
                                                       msg.content))
            else:
                logging.info('(PM) {} #{}: {}'.format(msg.author.name,
                                                      msg.author.id,
                                                      msg.content))

            cmd = self.bot.cmd_regex.search(msg.content)
            name = cmd.group('command').lower()
            args = cmd.group('args')

            if type(args) == str:
                if args == '':
                    args = []
                else:
                    args = [args]

            logging.info('Command parsed: {}({})'.format(name, args))

            if name == 'help':
                # Parse a help command
                if len(args) == 0:
                    # PixelBot help message
                    plugins = ''
                    for pl in self.bot.plugins.values():
                        plugins += '{} [{}]\n'.format(pl.name, pl.version)

                    info = (
                        '**PixelBot Help**\n'
                        'Version: {version}\n'
                        'Installed plugins:```{plugins}```'
                        'Commands: ```'
                        '{prefix}help [plugin] - Shows this message, or'
                        ' the plugin\'s help message if the "plugin" option'
                        ' is not empty.'
                        '```'
                    ).format(
                        version='0.1',
                        plugins=plugins,
                        prefix=self.bot.settings['options']['prefix']
                    )

                    await self.send_message(msg.channel, info)
                elif len(args) == 1:
                    # Plugin help message
                    plugin_name = args[0]

                    if plugin_name not in self.bot.plugins.keys():
                        await self.send_message(msg.channel,
                                                'Unknown plugin "{}".'
                                                .format(plugin_name))
                        return

                    plugin_obj = self.bot.plugins[plugin_name]
                    info = plugin_obj.generateHelp()
                    await self.send_message(msg.channel, info)
                else:
                    # Oops, error.
                    await self.send_message(msg.channel,
                                            'Invalid command syntax.')
                    return
            else:
                # Parse a plugin command
                for plugin in self.bot.plugins.values():
                    if cmd.group('command').lower() in plugin.cmds:
                        result = await plugin.cmds[name](plugin,
                                                         self,
                                                         msg,
                                                         args)

                        if result is not None:
                            logging.info('-> {}'.format(result))

                        break

    async def on_member_join(self, sv, user):
        # Run plugins "on_member_join" functions
        for plugin in self.bot.plugins.values():
            await plugin.on_member_join(self, user)

        logging.info('User {}#{} joined.'.format(user.name, user.id))

    async def on_member_remove(self, sv, user):
        # Run plugins "on_member_remove" functions
        for plugin in self.bot.plugins.values():
            await plugin.on_member_remove(self, user)

        logging.info('User {}#{} left.'.format(user.name, user.id))

    async def on_member_update(self, before, after):
        # Run plugins "on_member_update" functions
        for plugin in self.bot.plugins.values():
            await plugin.on_member_update(self, before, after)