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


# UI Debugging
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

        self._set_alarm()

    def _set_alarm(self, val=None):
        self.logger.debug('Setting alarm now')
        alarm_time = self.alarm.time
        seconds = seconds_until(alarm_time)
        self.logger.info('num seconds: {}'.format(seconds))


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
        self.index = 0
        application.home_screen.alarm_playing = True
        Clock.schedule_once(self._set_alarm, 120)
        self.play_greeting()

    def play_greeting(self, val=None):
        application.home_screen.greeting_label.text = ''
        index = self.index
        if index >= len(self.greetings):
            self.logger.info('Done playing greetings')
            application.home_screen.alarm_playing = False
            return

        self.logger.info('Playing greeting at index: {}'.format(index))
        greeting = self.greetings[index]
        logger.debug(self.greetings)
        if not greeting:
            logger.error('this greeting is no good')
            return

        if greeting.delay > 0 and not greeting.delayed:
            self.logger.info('Delaying for {} seconds'.format(greeting.delay))
            Clock.schedule_once(self.play_greeting, int(greeting.delay))
            greeting.delayed = True
            return

        greeting_text = greeting.display_text()
        if greeting_text:
            application.home_screen.greeting_label.text = greeting_text

        self.sound = greeting.sound_bit
        if not self.sound:
            self.logger.error('received empty sound')
            return

        self.sound.call_back = self.greeting_done
        self.sound.play()

        greeting.delayed = False

    def skip_greeting(self):
        if self.sound:
            self.sound.stop()
            self.sound.call_back = None

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

        # establish updates
        Config().HomeScreen.add_subscriber(self)
        Config().Alarm.add_subscriber(self)

        self.alarm_playing = False

        # view initialization
        self.load_views()

    def load_views(self):
        # custom widgets
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
        self.add_widget(self.bottom_left)

        # greeting info label
        self.top_center = AnchorLayout(anchor_x='center', anchor_y='top')
        self.greeting_label = Label(size_hint=(None, None), font_size=30)
        self.top_center.add_widget(self.greeting_label)
        self.add_widget(self.top_center)

    def get_widget(self, widg):
        logger.info('widg: {}'.format(widg))
        if widg not in HomeScreen.widget_positions:
            logger.exception('Widget not in a specified position')
            raise ValueError('Requested for invalid widget position: {}'.format(widg))

        widg_name = Config().HomeScreen.get(widg)
        position = HomeScreen.widget_positions[widg]
        anchor_x = position[0]
        anchor_y = position[1]


        if not widg_name:
            logger.warning('Widget {} not specified in configuration file, returning empty widget'.format(widg))
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
        elif heading == 'Alarm':
            # TODO: Make alarm actually updatable
            application.alarm_manager._set_alarm()

    def on_touch_down(self, touch):
        if touch.is_double_tap and self.alarm_playing:
            application.alarm_manager.skip_greeting()
            return True
        else:
            return super(HomeScreen, self).on_touch_down(touch)


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

        self.home_screen = HomeScreen(name='homescreen')

    def setup_logging(self):
        # logging
        logger = logging.getLogger('tock')
        logger.setLevel(logging.DEBUG)

        console_output = logging.StreamHandler()
        console_output.setLevel(logging.INFO)

        log_file = logging.handlers.RotatingFileHandler('tock.log', maxBytes=800000, backupCount=3)
        log_file.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_file.setFormatter(formatter)
        console_output.setFormatter(formatter)

        logger.addHandler(console_output)
        logger.addHandler(log_file)
        self.logger = logger


    def build(self):
        return self.home_screen

    def load_config(self, val=0):
        Config(self.config_file)



if __name__ == '__main__':
    logger = logging.getLogger('tock')
    application = Tock()
    application.run()
