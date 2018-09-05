import logging
import time
from subprocess import Popen
from datetime import datetime
from datetime import timedelta
from threading import Thread

from kivy.event import EventDispatcher


# utility methods


def seconds_until(time_str):
    current_timestamp = datetime.now()
    date_formats = ['%I:%M %p', '%H:%M']
    parsed_time = None
    print(time.strptime('10:40 PM', date_formats[0]))

    for d_format in date_formats:
        try:
            parsed_time = datetime.strptime(time_str, d_format)
        except ValueError as e:
            logging.getLogger('tock').info('Failed loading time: {}'.format(e))
            continue
        else:
            break

    if not parsed_time:
        return

    parsed_time = parsed_time.replace(year=current_timestamp.year, day=current_timestamp.day, month=current_timestamp.month)
    if current_timestamp > parsed_time:
        parsed_time += timedelta(days=1)

    logging.getLogger('tock').info('parsed time: {}'.format(parsed_time))

    return (parsed_time - current_timestamp).total_seconds()


class DotDict(dict):
    def __getitem__(self, item):
        if item not in self:
            return None
        else:
            return super(DotDict, self).__getitem__(item)

    def __getattr__(self, item):
        if item in self:
            return self[item]
        else:
            return None

    def __setattr__(self, key, value):
        self.__setitem__(key, value)


class SoundPlayer(object):
    def __init__(self, audio_file, audio_player=None):
        self.audio_file = audio_file
        self.proc = None
        self.play_thread = None
        self.call_back = None
        self.logger = logging.getLogger('tock')
        if not audio_player:
            self.audio_player = 'afplay'
        else:
            self.audio_player = audio_player

    def play(self):
        self.play_thread = Thread(target=self._play_audio)
        self.play_thread.start()

    def _play_audio(self):
        cmds = [self.audio_player, self.audio_file]
        cmd_str = ' '.join(cmds)
        self.logger.debug('Audio player command: {}'.format(cmd_str))
        try:
            self.proc = Popen(cmd_str, shell=True)
        except Exception as e:
            logging.getLogger('tock').error(
                'Failed to play audio file: {} with exception: {}'.format(self.audio_file, e))

        self.proc.wait()
        if self.call_back:
            self.call_back()
        self.logger.info('Finished playing audio: {}'.format(self.audio_file))

    def stop(self):
        if self.proc:
            self.proc.kill()




