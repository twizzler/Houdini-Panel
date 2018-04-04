from PIL import Image

from flask import Flask, request

from StringIO import StringIO
import requests
import os


class Avatar(object):
    def downloadImage(self, image, size=120):
        path = 'http://icer.ink/mobcdn.clubpenguin.com/game/items/images/paper/image/{}/{}.png'.format(size, image)

        print 'Downloading...', path

        dimg = requests.get(path)
        image_p = 'Avatar/paper/{}/{}.png'.format(size, image)

        p = '/'.join(image_p.split('/')[:-1])
        if not os.path.exists(p): os.makedirs(p)

        sprite = Image.open(StringIO(dimg.content))
        sprite.save(image_p)

        return sprite

    def initializeImage(self, items, size=120):
        path = 'Avatar/paper/{}/{}.png'.format(size, '{}')

        sprites = list()

        for i in items:
            if i == 0:
                sprites.append(Image.new('RGBA', (size, size), (0, 0, 0, 0)))
                continue

            if not os.path.exists(path.format(i)):
                sprites.append(self.downloadImage(i, size))
            else:
                sprite = Image.open(path.format(i))
                sprites.append(sprite)

        return sprites

    def buildAvatar(self, images):
        Avatar = images[0]
        for i in images[1:]:
            Avatar.paste(i, (0, 0), i)

        AvatarIO = StringIO()
        Avatar.save(AvatarIO, 'PNG', quality=100)
        AvatarIO.seek(0)

        return AvatarIO
