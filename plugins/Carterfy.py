#: vim set encoding=utf-8 :
##
 # Carterfy Plugin
 # Turns people at an image into random Carters.
 #
 # author William F.
 # version 0.02
##

# Imports
import PluginAPI as api

import discord
import face_recognition
import os
import random
import requests
import shutil
from PIL import Image, ImageOps


# Plugin code
class __plugin__(api.Plugin):
    global __plugin__, api
    global discord, face_recognition, os, random, requests, shutil, Image
    global ImageOps

    name = 'Carterfy'
    description = 'Turns people at an image into random Carters.'
    version = '0.02'
    author = 'William F.'
    default_data = {
        'image_id': 0
    }

    def __init__(self, bot):
        super().init(bot)

    # Methods
    async def on_ready(self, client):
        self.log('Initializing...')

        # Reset our data
        self.log('Resetting data...')
        self.data['image_id'] = 0
        self.saveData()

        # TODO: Clear the cache
        self.log('Clearing image cache...')

        self.log('Initialized.')

    # Commands
    @api.command('carterfy', mod=False)
    async def cmd_carterfy(self, client, msg, args):
        '''Add Carter to the image.'''

        if len(msg.attachments) != 1:
            await client.send_message(msg.channel,
                                      'Please attach an image to the command.')
            return

        self.data['image_id'] += 1
        self.saveData()

        attachment = msg.attachments[0]
        url = attachment['url']
        extension = attachment['filename'].rpartition('.')[-1]
        org_name = '{}/images/{}.{}'.format(self.getDataFolder(),
                                            self.data['image_id'],
                                            extension)

        # Download the attached image
        r = requests.get(url, stream=True, headers={'User-agent': 'Mozilla/5.0'})

        if r.status_code == 200:
            with open(org_name, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        else:
            await client.send_message(msg.channel,
                                      'Oops, something went wrong! Try again please.')
            return

        # Recognize faces in the image
        image = face_recognition.load_image_file(org_name)
        faces = face_recognition.face_locations(image)

        if len(faces) > 0:
            # If we found any faces, paste a random carter on top of them
            original = Image.open(org_name)

            # For each face that we found:
            for face_location in faces:
                # Load a random carter
                carter_image = Image.open('{}/carter/{}.png'
                                          .format(self.getDataFolder(),
                                                  random.randint(0, 14)))

                # Resize it to the size of the face (slightly bigger than it, actually)
                top, right, bottom, left = face_location
                face_image = Image.fromarray(image[top:bottom, left:right])
                face_w, face_h = face_image.size

                carter_image = carter_image.resize((face_w + 50, face_h + 50),
                                                   Image.NEAREST)

                # 50% chance of mirroring it
                if random.randint(0, 1) == 0:
                    carter_image = ImageOps.mirror(carter_image)

                # Then paste it on top of the face
                original.paste(carter_image, (left - 25, top - 25), carter_image)

            # Then save and send back the result
            out_name = '{}/images/{}_out.png'.format(self.getDataFolder(),
                                                    self.data['image_id'])
            original.save(out_name, 'PNG')

            await client.send_file(msg.channel, out_name)

            # Delete the image afterwards
            os.remove(out_name)
        else:
            # Otherwise tell them we couldn't do it
            await client.send_message(msg.channel, 'I found no faces in this image. :/')

        # Delete the image afterwards
        os.remove(org_name)
