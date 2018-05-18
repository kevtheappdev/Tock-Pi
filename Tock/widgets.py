import time
import json
import requests
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.image import AsyncImage
from kivy.graphics import Color
from kivy.graphics import Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.layout import Layout



class WeatherLabel(Label):
    def __init__(self, **kwargs):
        super(WeatherLabel, self).__init__(**kwargs)
        self.fetch()
        Clock.schedule_interval(self.fetch, 60 * 60)
        self.font_size = 50

    def fetch(self, val=0):
        # TODO: Avoid hard coding
        req = requests.get("http://api.openweathermap.org/data/2.5/weather?q=Cupertino&appid=1c51e68c4823e92a75f2590404fd6634&units=imperial")
        data = req.json()
        print(data)
        if 'error' in data:
            print('ERROR: Could not load weather data: {}'.format(data))

        # TODO: fix this is gacky
        temp = int(data['main']['temp'])
        print(temp)
        self.text = '{} °'.format(temp)


class TockClock(Label):
    def __init__(self, seconds=False, military=False, **kwargs):
        super(TockClock, self).__init__(**kwargs)
        self.seconds = seconds
        self.military = military
        self.font_size = 150
        self.text = self.time_str()
        Clock.schedule_interval(self.update, 0.5)

    def update(self, val):
        time_data = self.time_str()
        self.text = time.strftime(time_data)

    def time_str(self):

        if self.military:
            t_str = '%H:%M'
        else:
            t_str = '%-I:%M %p'

        if self.seconds:
            return t_str + ':%S'
        else:
            return t_str


class TockDate(Label):
    def __init__(self, **kwargs):
        super(TockDate, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.font_size = 50
        self.size = (300, 100)
        Clock.schedule_interval(self.date_str, 0.5)

    def date_str(self, val=0):
        self.text = time.strftime('%b %d')

