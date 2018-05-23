import requests

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.clock import Clock


class NasaApod(FloatLayout):
    def __init__(self, show_desc=True, **kwargs):
        super(NasaApod, self).__init__(**kwargs)
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
        # TODO make this async, section off the url
        print('Making request')
        req = requests.get("https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY")
        data = req.json()

        if 'error' in data:
            print('ERROR: Could not load: {}'.format(data['error']))
            # TODO: Implement logging and have some kind of fall back
        if 'hdurl' in data:
            print('image url: {}'.format(data['hdurl']))
            self.image.source = data['hdurl']
        else:
            self.image.source = 'https://apod.nasa.gov/apod/image/1805/Tarantula_HubbleLacrue_3204.jpg'
        if 'title' in data:
            self.title_label.text = data['title']