import kivy
kivy.require('1.10.1') # replace with your current kivy version !

from kivy.clock import Clock
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.window import Window
from kivy.graphics import Rectangle
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.image import AsyncImage
from kivy.lang.builder import Builder

# Builder.load_string('''<Widget>:
#     canvas.after:
#         Line:
#             rectangle: self.x+1,self.y+1,self.width-1,self.height-1
#             dash_offset: 5
#             # dash_length: 3''')

from widgets import *


class HomeScreen(FloatLayout):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)

        # TODO: load from config

        # view initialization
        backdrop = AnchorLayout(anchor_x='center', anchor_y='center')
        self.image = AsyncImage()
        backdrop.add_widget(self.image)

        bottom_center = AnchorLayout(anchor_x='center', anchor_y='bottom')
        self.title_label = Label(size_hint=(None, None))
        bottom_center.add_widget(self.title_label)

        center = AnchorLayout(anchor_x='center', anchor_y='center')
        self.clock = TockClock()
        center.add_widget(self.clock)

        top_left = AnchorLayout(anchor_x='left', anchor_y='top')
        self.weather_label = WeatherLabel(size_hint=(None, None))
        top_left.add_widget(self.weather_label)

        top_right = AnchorLayout(anchor_x='right', anchor_y='top')
        self.date_label = TockDate()
        top_right.add_widget(self.date_label)

        self.add_widget(backdrop)
        self.add_widget(bottom_center)
        self.add_widget(center)
        self.add_widget(top_left)
        self.add_widget(top_right)

        self.image_request()
        Clock.schedule_interval(self.image_request, 86400)

    def image_request(self, val=0):
        # TODO make this async, section off the url
        req = requests.get("https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY")
        data = req.json()
        if 'error' in data:
            print('ERROR: Could not load: {}'.format(data['error']))
            # TODO: Implement logging and have some kind of fall back
        if 'hdurl' in data:
            print('image url: {}'.format(data['hdurl']))
            self.image.source = data['hdurl']
        if 'title' in data:
            self.title_label.text = data['title']


class Tock(App):
    def build(self):
        return HomeScreen()


if __name__ == '__main__':
    Tock().run()
