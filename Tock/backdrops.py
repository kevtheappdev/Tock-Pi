import requests
import logging

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.clock import Clock


class NasaApod(FloatLayout):
    def __init__(self, show_desc=True, **kwargs):
        super(NasaApod, self).__init__(**kwargs)
        self.logger = logging.getLogger('tock')

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
        if 'hdurl' in data:
            self.logger.info('Found url in data: {}'.format(data['hdurl']))
            self.image.source = data['hdurl']
            # set title only if we have an image
            if 'title' in data:
                self.title_label.text = data['title']
        else:
            default_image = 'https://apod.nasa.gov/apod/image/1805/Tarantula_HubbleLacrue_3204.jpg'
            self.logger.warning('Failed to find valid image url, defaulting to: {}'.format(default_image))
            self.image.source = default_image
