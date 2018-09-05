import time
import json
import requests
import logging
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy import Logger
from kivy.uix.image import AsyncImage
from kivy.graphics import Color
from kivy.graphics import Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.layout import Layout

from utils import DotDict
from config import *


class WeatherLabel(Label):
    def __init__(self, **kwargs):
        super(WeatherLabel, self).__init__(**kwargs)
        self.logger = logging.getLogger('tock')
        self.font_size = 50

        self.size_hint = (None, None)

        self.fetch()
        Clock.schedule_interval(self.fetch, 60 * 60)

    def fetch(self, val=0):
        # TODO: Avoid hard coding
        req = requests.get("http://api.openweathermap.org/data/2.5/weather?q=Austin&appid=1c51e68c4823e92a75f2590404fd6634&units=imperial")
        data = DotDict(req.json())
        if 'error' in data:
            self.logger.error('Error fetching weather: {}'.format(data['error']))
            return

        # TODO: fix this it's gacky
        temp = int(data['main']['temp'])
        self.logger.debug('Parsed temperature: {}'.format(temp))
        self.text = '{} °'.format(temp)


class TockClock(Label):
    def __init__(self, seconds=False, military=False, font_size=150, **kwargs):
        super(TockClock, self).__init__(**kwargs)
        self.seconds = seconds
        self.military = military
        self.font_size = font_size
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
        # TODO make this the real update time
        Clock.schedule_interval(self.date_str, 0.5)

    def date_str(self, val=0):
        self.text = time.strftime('%b %d')

class BrightnessButton(Button):
    brightnesses = [('Full', 100), ('Medium', 75), ('Night', 30)]

    def __init__(self, **kwargs):
        super(BrightnessButton, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.font_size = 25
        self.size = (150, 50)
        self.current_brightness = 0
        self.text = self.brightnesses[self.current_brightness][0]
        self.background_color = (0, 0, 0, 0)
        self.bind(on_press=self.pressed)

    def pressed(self, instance):
        try:
            import rpi_backlight as bl
        except ImportError:
            # TODO: add logging here
            print('No library to change brightness')
            return

        self.current_brightness = (self.current_brightness + 1) % len(self.brightnesses)
        brightness_data = self.brightnesses[self.current_brightness]
        brightness = brightness_data[1]
        self.text = brightness_data[0]
        bl.set_brightness(brightness)

        self.current_brightness = (self.current_brightness + 1) % len(self.brightnesses)
        brightness_data = self.brightnesses[self.current_brightness]
        brightness = brightness_data[1]
        self.text = brightness_data[0]
        bl.set_brightness(brightness)

        return True

class NextAlarmLabel(Label):
    def __init__(self, **kwargs):
        super(NextAlarmLabel, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (225, 50)
        self.font_size = 25
        self.update_time()
        Clock.schedule_interval(self.update_time, 1)

    def update_time(self, val=0):
        # peridically fetch time to update
        self.text = '{} Alarm'.format(Config().Alarm.time)

