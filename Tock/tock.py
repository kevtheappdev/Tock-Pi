import kivy
kivy.require('1.10.1') # replace with your current kivy version !


from kivy.clock import Clock
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout

# from kivy.lang.builder import Builder

# Builder.load_string('''<Widget>:
#     canvas.after:
#         Line:
#             rectangle: self.x+1,self.y+1,self.width-1,self.height-1
#             dash_offset: 5
#             # dash_length: 3''')

from widgets import *
from backdrops import *
from config import *


class HomeScreen(FloatLayout, Subscriber):
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
            raise ValueError('Requested for invalid widget position: {}'.format(widg))

        widg_name = Config().HomeScreen.get(widg)
        position = HomeScreen.widget_positions[widg]
        anchor_x = position[0]
        anchor_y = position[1]

        print('Getting widget: {}'.format(widg))

        if not widg_name:
            return AnchorLayout(anchor_x=anchor_x, anchor_y=anchor_y)

        try:
            widg_class = eval(widg_name)
        except NameError:
            print('ERROR: Could not find class {}'.format(widg_name))
            return None
        else:
            if callable(widg_class):
                widget = widg_class()
            else:
                widget = widg_class


            layout = AnchorLayout(anchor_x=anchor_x, anchor_y=anchor_y)
            layout.add_widget(widget)
            self.widgets[widg] = layout
            print('returning {}'.format(layout))
            return layout

    def update(self, updated_key):
        print('updating home screen')
        if updated_key in self.widgets:
            existing_widget = self.widgets[updated_key]
            self.remove_widget(existing_widget)

        updated_widget = self.get_widget(updated_key)
        if updated_widget:
            self.add_widget(updated_widget)



class Tock(App):
    def __init__(self, config_file='tock.config', **kwargs):
        super(Tock, self).__init__(**kwargs)
        self.config_file = config_file
        self.load_config()
        Clock.schedule_interval(self.load_config, 15)

    def build(self):
        return HomeScreen()

    def load_config(self, val=0):
        Config(self.config_file)



if __name__ == '__main__':
    Tock().run()
