import kivy
kivy.require('1.10.1') # replace with your current kivy version !

import logging
from logging import handlers

from kivy.clock import Clock
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import ScreenManager, Screen

# from kivy.lang.builder import Builder

# Builder.load_string('''<Widget>:
#     canvas.after:
#         Line:
#             rectangle: self.x+1,self.y+1,self.width-1,self.height-1
#             dash_offset: 5
#             # dash_length: 3''')


from config import *
from utils import *


class AlarmManager(object):
    def __init__(self):
        self.alarm = Config().Alarm

        if not self.alarm:
            raise ValueError('Configuration file not instantiated')

        alarm_time = self.alarm.time
        seconds = seconds_until(alarm_time)

        self.greetings = self.alarm.greetings

        if not seconds:
            raise ValueError("Yeah we're gonna need a valid time value.... and we don't... :(")
        if seconds > 300:
            Clock.schedule_interval(self.fetch_greetings, seconds - 300)
        else:
            self.fetch_greetings(self.wakeup, seconds)

        Clock.schedule_interval(self.wakeup, seconds)

    def wakeup(self):
        application.sm.current = 'alarm'


    def fetch_greetings(self):
        for greeting in self.greetings:
            greeting_obj = eval_widg(greeting)
            greeting_obj.fetch()


############################################
#                 Screens                  #
############################################

class AlarmScreen(Screen, Subscriber):
    def __init__(self, **kwargs):
        super(AlarmScreen, self).__init__(**kwargs)
        self.add_widget(Label(text='Wake Up!!'))

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

    def update(self, updated_key):
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
        self.sm.add_widget(HomeScreen(name='homescreen'))
        self.sm.add_widget(AlarmScreen(name='alarm'))

    def setup_logging(self):
        # logging
        logger = logging.getLogger('tock')
        logger.setLevel(logging.DEBUG)

        console_output = logging.StreamHandler()
        console_output.setLevel(logging.DEBUG)

        log_file = logging.handlers.RotatingFileHandler('tock.log', maxBytes=80000, backupCount=10)
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
