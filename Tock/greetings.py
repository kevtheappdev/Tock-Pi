import logging
import requests

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from google.cloud import texttospeech as tts
from kivy.core.audio import SoundLoader

from utils import *
from config import *


class Greeting(object):
    """ Abstract base class, provides method for each morning wakeup greeting
    """

    def __init__(self, greeting_name):
        self.greeting_name = greeting_name
        self.sound_bit = None
        self.logger = logging.getLogger('tock')

    def fetch(self):
        """ Fetch data necessary for greeting
        :return: None
        """
        pass

    def generate_sound_bit(self, speech_text):
        client = tts.TextToSpeechClient()
        input_text = tts.types.SynthesisInput(text=speech_text)
        voice = tts.types.VoiceSelectionParams(
            language_code='en-US',
            ssml_gender=tts.enums.SsmlVoiceGender.FEMALE)
        audio_config = tts.types.AudioConfig(
            audio_encoding=tts.enums.AudioEncoding.MP3)

        response = client.synthesize_speech(input_text, voice, audio_config)

        out_file_name = '{}.mp3'.format(self.greeting_name)
        with open(out_file_name, 'wb') as out:
            out.write(response.audio_content)

        return SoundLoader.load(out_file_name)

    def display_widget(self):
        """ Returns the widget to display in morning greeting scroll view
        :return: kivy.uix.widget.Widget
        """
        return Label(text=self.greeting_name)


class WakeUpGreeting(Greeting):
    def __init__(self):
        super(WakeUpGreeting, self).__init__('Wake Up!')
        file_name = Config().Alarm.sound
        self.sound_bit = SoundLoader.load(filename=file_name)


class WeatherGreeting(Greeting):
    def __init__(self):
        super(WeatherGreeting, self).__init__(greeting_name='Weather')
        self.weather_url = Config().Constants.weather_query
        self.logger = logging.getLogger('tock')
        self.read_text = ''

    def fetch(self):
        self.logger.info('fetching weather greeting')
        if not self.weather_url:

            return
        req = requests.get(self.weather_url)
        data = DotDict(req.json())
        print(data)
        if 'error' in data:
            print('error fetching')
            self.logger.error('Error fetching weather: {}'.format(data['error']))

        weather_details = data.weather
        if len(weather_details) < 1:
            return

        description = weather_details[0]['description']
        todays_high = data.main['temp_max']
        todays_low = data.main['temp_min']
        temp = data.main['temp']

        self.read_text = "It's {} degrees in Cupertino with {}. Today's high is {}, and the low will be {}".format(int(temp), description, int(todays_high), int(todays_low))
        self.sound_bit = self.generate_sound_bit(self.read_text)
