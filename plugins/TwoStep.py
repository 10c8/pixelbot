#: vim set encoding=utf-8 :
##
 # TwoStep Plugin
 # Protects the server from VPN/proxy users.
 #
 # author William F., Henry Jeff
 # version 0.3
 # copyright MIT
##

# Imports
import PluginAPI as api

import discord
import json
import requests
import threading
from datetime import datetime, timedelta
from random import randint
from bottle import route, post, request, static_file, run


# Plugin code
class __plugin__(api.Plugin):
    global __plugin__, api
    global discord, json, requests, threading, datetime, timedelta
    global randint, route, post, request, static_file, run

    name = 'TwoStep'
    description = 'Protects the server from VPN/proxy users.'
    version = '0.3'
    author = 'William F.'
    default_data = {
        'codes': {},
        'ok': [],
        'bad': []
    }

    def __init__(self, bot):
        api.Plugin.init(self, bot)

    # Methods
    async def on_ready(self, client):
        self.log('Initializing...')

        @route('/')
        def index():
            return static_file('index.html', root='data/views/')

        @route('/static/<filepath:path>')
        def server_static(filepath):
            return static_file(filepath, root='data/static/')

        @post('/auth')
        def auth():
            uid = request.forms.get('uid')
            pin = request.forms.get('pin')

            if uid not in self.data['codes'].keys():
                result = {
                    'status': 'error',
                    'error': 'Invalid UID.'
                }
            elif pin != self.data['codes'][uid]:
                result = {
                    'status': 'error',
                    'error': 'Wrong PIN-code.'
                }
            else:
                # Get user IP
                forwarded_addr = request.environ.get('HTTP_X_FORWARDED_FOR')
                remote_addr = request.environ.get('REMOTE_ADDR')
                ip = forwarded_addr or remote_addr

                # Check it on the database
                check = self.check_ip(ip)

                if not check:
                    result = {
                        'status': 'error',
                        'error': 'Something went wrong. Try again.'
                    }
                elif check['status'] == 'error':
                    result = {
                        'status': 'error',
                        'error': check['message']
                    }
                else:
                    # Check for a proxy IP
                    if float(check['result']) > 0.99 or\
                       check['BadIP'] == 1:
                        # Bad IP, tell the mods
                        self.data['bad'].append(uid)

                        result = {
                            'status': 'error',
                            'error': (
                                'Our system detected that you might be'
                                ' using a proxy, which is not allowed'
                                ' in this server. If you believe that'
                                ' this was a mistake, don\'t worry; our'
                                ' mods will catch it and verify you'
                                ' manually if that\'s the case. Just be'
                                ' patient.'
                            )
                        }
                    else:
                        self.data['ok'].append(uid)

                        result = {
                            'status': 'success',
                            'error': ''
                        }

            return json.dumps(result)

        self.log('Starting webserver...')

        try:
            threading.Thread(target=run,
                             kwargs=dict(host='0.0.0.0',
                                         port=8080)).start()
            self.log('Done.')
        except Exception as e:
            self.log('Error.')
            self.critical(e)
            exit(1)

        self.log('Initialized.')

    async def on_member_join(self, client, user):
        # Server
        sv = list(client.servers)[0]

        # Role used for verification
        unverified = discord.Role(server=sv,
                                  id=self.getConfig('unverified_role'))

        # Set them to "Unverified" as soon as they join
        await client.add_roles(user, unverified)

        # Generate their PIN-code
        pin = ''.join([str(randint(0, 9)) for _ in range(6)])
        while pin in self.data['codes'].values():
            pin = ''.join([str(randint(0, 9)) for _ in range(6)])

        self.data['codes'][str(user.id)] = pin

        self.log('[pin] {} ({}): {}'.format(user.name, user.id, pin))

        # Send the help message
        auth_msg = (
            'Welcome to the Pixel Art server, <@{id}>!\n\n'
            'Due to recent ban circumvention issues caused by malicious'
            ' users, we are sorry to inform you that we now require'
            ' newcomers to confirm their account via the following'
            ' procedure:\n\n'
            '**1.** Visit the following link:'
            ' http://108.14.46.160:8080/?uid={id}\n'
            '**2.** Enter the following generated PIN-code: ***{code}***\n'
            '**3.** Done! :smiley:'
        )

        await client.send_message(user, auth_msg.format(
            id=user.id,
            code=' '.join(list(pin))
        ))

        # self.saveData()

    # Utils
    def check_ip(self, ip):
        ip_api = (
            'http://check.getipintel.net/check.php?'
            'ip={ip}'
            '&contact={contact}'
            '&flags={flags}'
            '&oflags={oflags}'
            '&format=json'
        )

        # Request an IP check
        r = requests.get(ip_api.format(ip=ip,
                                       contact=self.getConfig('contact'),
                                       flags=self.getConfig('flags'),
                                       oflags=self.getConfig('oflags')))

        if r.status_code != 200:
            # Request failed
            self.critical('Failed to check IP.')
            return False
        else:
            # Request successful
            result = json.loads(r.text)
            self.log('IP check for {} returned "{}".'.format(ip, result))
            return result

    # Tasks
    @api.task('VerifyUsers', 1)
    async def task_VerifyUsers(self, client):
        await client.wait_until_ready()

        # Server
        sv = list(client.servers)[0]

        # Welcome channel
        welcome_ch = discord.Object(id=self.getConfig('welcome_ch'))
        mods_ch = discord.Object(id=self.getConfig('mods_ch'))

        for i, uid in enumerate(self.data['ok']):
            user = sv.get_member(uid)

            # Role used for verification
            verified = discord.Role(server=sv,
                                    id=self.getConfig('verified_role'))

            # Verify user
            await client.replace_roles(user, verified)

            # And greet them
            await client.send_message(welcome_ch,
                                      self.getConfig('welcome_msg')
                                      .format(username=user.id,
                                              number=sv.member_count))
            await client.send_message(user, self.getConfig('welcome_pm'))

            self.data['ok'][i] = ''

        for i, uid in enumerate(self.data['bad']):
            user = sv.get_member(uid)
            await client.send_message(mods_ch,
                                      'User <@{}> requires verification.'
                                      .format(user.id))

            self.data['bad'][i] = ''

        # Clean the OK and BAD lists
        self.data['ok'] = [x for x in self.data['ok'] if x != '']
        self.data['bad'] = [x for x in self.data['bad'] if x != '']
