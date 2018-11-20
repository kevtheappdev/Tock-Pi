import os
import requests
import logging
import random

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.clock import Clock

IMAGE_LOG = 'image_log.txt'


class NasaApod(FloatLayout):
    def __init__(self, show_desc=True, **kwargs):
        super(NasaApod, self).__init__(**kwargs)
        self.logger = logging.getLogger('tock')
        self.previous_images = self.load_image_log()

        backdrop = AnchorLayout(anchor_x='center', anchor_y='center')
        self.image = AsyncImage()
        backdrop.add_widget(self.image)

        bottom_center = AnchorLayout(anchor_x='center', anchor_y='bottom')
        if show_desc:
            self.title_label = Label(size_hint=(None, None))
            bottom_center.add_widget(self.title_label)

        self.add_widget(backdrop)
        self.add_widget(bottom_center)

        self.image_request()
        Clock.schedule_interval(self.image_request, 86400)

    def image_request(self, val=0):
        self.logger.info('Fetching NASA image of the day')
        # TODO make this async, section off the url
        req = requests.get("https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY")
        data = req.json()

        if 'error' in data:
            # TODO: have some kind of a fall back
            self.logger.error('Encountered error with APOD API call: {}'.format(data['error']))
        if 'url' in data:
            self.logger.info('Found url in data: {}'.format(data['url']))
            url = data['url']
            self.logger.info('Recieved ')
            # skip if it returns a video
            if 'youtube' in url:
                self.set_default()
                return

            self.image.source = data['url']
            self.add_image(data['url'])

            if 'title' in data:
                self.title_label.text = data['title']
        else:
            self.set_default()

    def load_image_log(self):
        if not os.path.exists(IMAGE_LOG):
            return list()

        with open(IMAGE_LOG, 'r') as f:
            images = f.readlines()
        return images

    def add_image(self, image_url):
        self.previous_images.append(image_url)
        with open(IMAGE_LOG, 'w') as f:
            f.write('\n'.join(self.previous_images))

    def set_default(self):
        if len(self.previous_images) == 0:
            default_image = 'https://apod.nasa.gov/apod/image/1805/Tarantula_HubbleLacrue_3204.jpg'
        else:
            default_image = random.choice(self.previous_images)

        self.logger.warning('Failed to find valid image url, defaulting to: {}'.format(default_image))
        self.image.source = default_image
