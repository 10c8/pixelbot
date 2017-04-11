#: vim set encoding=utf-8 :
##
 # TwoStep Plugin
 # Protects the server from VPN/proxy users.
 #
 # author William F., Henry Jeff
 # version 0.1
 # copyright MIT
##

# Imports
import PluginAPI as api
import discord


# Plugin code
class __plugin__(api.Plugin):
    global __plugin__, api
    global discord

    name = 'TwoStep'
    description = 'Protects the server from VPN/proxy users.'
    version = '0.1'
    author = 'William F.'
    default_data = {
        'codes': {}
    }

    def __init__(self, bot):
        api.Plugin.init(self, bot)

    async def on_ready(self, client):
        # TODO:
        # [x] Webserver
        # [ ] PIN-code verification
        # [ ] IP check

        import json
        import threading
        from bottle import get, post, request, run

        self.log('Initializing...')

        @post('/auth')
        def auth():
            return json.dumps({
                'status': 'success'
            })

        self.log('Starting webserver...')

        try:
            threading.Thread(target=run,
                             kwargs=dict(host='localhost',
                                         port=8080)).start()
            self.log('Done.')
        except Exception as e:
            self.log('Error.')
            self.critical(e)
            exit(1)

        self.log('Initialized.')

    async def on_member_join(self, client, user):
        from datetime import datetime, timedelta

        # Server
        sv = list(client.servers)[0]

        # Roles used for verification
        unverified_role = discord.Role(server=sv,
                                       id=self.unverified_role)
        verified_role = discord.Role(server=sv,
                                     id=self.verified_role)

    async def on_message(self, client, msg):
        code_ch = discord.Object(id=self.getConfig('code_ch'))

        if msg.channel != code_ch:
            return
