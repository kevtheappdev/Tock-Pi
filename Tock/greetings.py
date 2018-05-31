from kivy.uix.widget import Widget


class Greeting(object):
    """ Abstract class, provides method for each morning wakeup greeting
    """
    def fetch(self):
        """ Fetch data necessary for greeting
        :return: None
        """
        pass

    def display_widget(self):
        """ Returns the widget to display in morning greeting scroll view
        :return: kivy.uix.widget.Widget
        """
        pass

    def speak_str(self):
        """ Returns string to bew read aloud as part of morning greeting
        :return: str
        """
        pass


class WeatherGreeting(Greeting):
    pass
