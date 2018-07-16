import kivy
kivy.require('1.10.1')
import time

import logging
from logging import handlers

from io import StringIO

from kivy.clock import Clock
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.core.audio import SoundLoader
from google.cloud import texttospeech as tts


# from kivy.lang.builder import Builder
#
# Builder.load_string('''<Widget>:
#     canvas.after:
#         Line:
#             rectangle: self.x+1,self.y+1,self.width-1,self.height-1
#             dash_offset: 5
#             # dash_length: 3''')


from config import *
from utils import *
from greetings import *
from widgets import *
from eval import eval_widg


class AlarmManager(object):
    def __init__(self):
        self.alarm = Config().Alarm
        self.logger = logging.getLogger('tock')
        self.index = 0
        self.sound = None

        if not self.alarm:
            raise ValueError('Configuration file not instantiated')

        alarm_time = self.alarm.time
        seconds = seconds_until(alarm_time)
        print('num seconds: {}'.format(seconds))


        greeting_implementations = self.alarm.greetings
        if not greeting_implementations:
            greeting_implementations = []

        self.greetings = [eval_widg(greeting) for greeting in greeting_implementations]

        file_name = self.alarm.sound
        self.sound_loader = SoundLoader.load(filename='alarm.wav')

        if not seconds:
            raise ValueError("Yeah we're gonna need a valid time value.... and we don't... :(")

        if seconds > 300:
            Clock.schedule_once(self.fetch_greetings, seconds - 300)
        else:
            self.fetch_greetings()
        print('Will wake up in {} seconds'.format(seconds))
        Clock.schedule_once(self.wakeup, seconds)

    def fetch_greetings(self, val=0):
        for greeting in self.greetings:
            if not greeting:
                continue
            greeting.fetch()

    def wakeup(self, val):
        self.logger.info('Waking up now...')
        application.sm.current = 'alarm'
        self.play_greeting()
        Clock.schedule_interval(self.reset, 60*60)

    def reset(self, val):
        application.sm.current = 'homescreen'

    def play_greeting(self):
        index = self.index
        if index >= len(self.greetings):
            return

        greeting = self.greetings[index]
        print(self.greetings)
        if not greeting:
            print('this greeting is no good')
            return

        widg_display = greeting.display_widget()
        if widg_display:
            application.alarm_screen.display_widget(widg_display)

        self.sound = greeting.sound_bit
        if not self.sound:
            print('received empty sound')
            return

        self.sound.call_back = self.greeting_done
        self.sound.play()

    def skip_greeting(self):
        if self.sound:
            self.sound.stop()

        self.index += 1
        self.play_greeting()

    def cancel_wakeup(self):
        if self.sound:
            self.sound.stop()

    def greeting_done(self):
        time.sleep(2)
        self.index += 1
        self.play_greeting()

############################################
#                 Screens                  #
############################################

class AlarmScreen(Screen, Subscriber):
    def __init__(self, **kwargs):
        super(AlarmScreen, self).__init__(**kwargs)
        self.box_layout = BoxLayout(orientation='horizontal')

        self.left_area = AnchorLayout(anchor_x='center', anchor_y='center')
        self.left_area.add_widget(TockClock(font_size=75))

        self.right_area = AnchorLayout(anchor_x='center', anchor_y='center')

        self.box_layout.add_widget(self.left_area)
        self.box_layout.add_widget(self.right_area)

        self.add_widget(self.box_layout)

        self.main_widg = None

    def display_widget(self, widg):
        if self.main_widg:
            self.right_area.remove_widget(self.main_widg)

        self.main_widg = widg
        self.right_area.add_widget(widg)

    def on_touch_down(self, touch):
        if touch.is_double_tap:
            application.alarm_manager.skip_greeting()
        elif touch.is_triple_tap:
            application.alarm_manager.cancel_wakeup()
            application.sm.current = 'homescreen'

class HomeScreen(Screen, Subscriber):
    widget_positions = {
         'backdrop' : ('center', 'center'),
         'top-left' : ('left', 'top'),
         'top-right': ('right', 'top'),
         'bottom-left': ('left', 'bottom'),
         'bottom-right': ('right', 'bottom'),
         'clock'  : ('center', 'center')
    }

    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.widgets = dict()

        Config().HomeScreen.add_subscriber(self)
        Config().Alarm.add_subscriber(self)

        # view initialization
        self.load_views()

    def load_views(self):
        self.backdrop = self.get_widget('backdrop')
        self.top_left = self.get_widget('top-left')
        self.top_right = self.get_widget('top-right')
        self.bottom_left = self.get_widget('bottom-left')
        self.bottom_right = self.get_widget('bottom-right')
        self.clock = self.get_widget('clock')

        self.add_widget(self.backdrop)
        self.add_widget(self.clock)
        self.add_widget(self.top_left)
        self.add_widget(self.top_right)
        self.add_widget(self.bottom_right)


    def get_widget(self, widg):
        if widg not in HomeScreen.widget_positions:
            logger.exception('Widget not in a specified position')
            raise ValueError('Requested for invalid widget position: {}'.format(widg))

        widg_name = Config().HomeScreen.get(widg)
        position = HomeScreen.widget_positions[widg]
        anchor_x = position[0]
        anchor_y = position[1]


        if not widg_name:
            logger.warning('Widget not specified in configuration file, returning empty widget')
            return AnchorLayout(anchor_x=anchor_x, anchor_y=anchor_y)

        widget = eval_widg(widg_name)

        layout = AnchorLayout(anchor_x=anchor_x, anchor_y=anchor_y)
        layout.add_widget(widget)
        self.widgets[widg] = layout
        return layout

    def update(self, heading, updated_key):
        if heading == 'HomeScreen':
            if updated_key in self.widgets:
                existing_widget = self.widgets[updated_key]
                self.remove_widget(existing_widget)

            updated_widget = self.get_widget(updated_key)
            if updated_widget:
                self.add_widget(updated_widget)


############################################
#                 Application              #
############################################

class Tock(App):
    def __init__(self, config_file='tock.config', **kwargs):
        super(Tock, self).__init__(**kwargs)
        self.setup_logging()
        self.config_file = config_file
        self.load_config()
        self.alarm_manager = AlarmManager()
        # refresh config
        Clock.schedule_interval(self.load_config, 15)

        # Multiple screens
        self.sm = ScreenManager()
        self.home_screen = HomeScreen(name='homescreen')
        self.alarm_screen = AlarmScreen(name='alarm')
        self.sm.add_widget(self.home_screen)
        self.sm.add_widget(self.alarm_screen)
        # Clock.schedule_once(self.change_screens, 15)

    def setup_logging(self):
        # logging
        logger = logging.getLogger('tock')
        logger.setLevel(logging.DEBUG)

        console_output = logging.StreamHandler()
        console_output.setLevel(logging.DEBUG)

        log_file = logging.handlers.RotatingFileHandler('tock.log', maxBytes=800000, backupCount=3)
        log_file.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_file.setFormatter(formatter)
        console_output.setFormatter(formatter)

        logger.addHandler(console_output)
        logger.addHandler(log_file)
        self.logger = logger

    def change_screens(self, val):
        self.sm.current = 'alarm'

    def build(self):
        return self.sm

    def load_config(self, val=0):
        Config(self.config_file)



if __name__ == '__main__':
    logger = logging.getLogger('tock')
    application = Tock()
    application.run()
