import re
import collections
import logging

from utils import *


class Subscriber(object):
    def update(self, updated_key):
        pass


class Config(object):
    _instance = None
    logger = logging.getLogger('tock')

    class ConfigSection(DotDict):
        def __init__(self, heading, **kwargs):
            super(Config.ConfigSection, self).__init__(**kwargs)
            self.subscribers = list()
            self.heading = heading

        def add_subscriber(self, subscriber):
            if isinstance(subscriber, Subscriber):
                self.subscribers.append(subscriber)

        def __setitem__(self, key, value):
            super(Config.ConfigSection, self).__setitem__(key, value)
            self.notify(key)

        def __delitem__(self, key):
            super(Config.ConfigSection, self).__delitem__(key)
            self.notify(key)

        def notify(self, key):
            Config.logger.debug('Notifying {} subscribers..'.format(len(self.subscribers)))
            for subscriber in self.subscribers:
                Config.logger.debug('Subscriber: {}'.format(subscriber))
                subscriber.update(self.heading, key)

    class ConfigInstance(DotDict):
        heading_pattern = '\[([a-zA-Z]+)\]'

        def __init__(self, config_file, **kwargs):
            super(Config.ConfigInstance, self).__init__(**kwargs)
            self.load_config(config_file)

        def load_config(self, config_file):
            # load file
            with open(config_file, 'r') as cf:
                config_lines = cf.readlines()

            current_section = None
            for line in config_lines:
                if not line.strip():
                    continue

                if line.strip()[0] == '#':
                    continue

                heading_srch = re.search(Config.ConfigInstance.heading_pattern, line)
                if heading_srch:
                    heading = heading_srch.group(1)

                    if heading in self:
                        Config.logger.debug('already exists: {} type: {}'.format(heading, type(self[heading])))
                        current_section = self[heading]
                    else:
                        Config.logger.debug('Found new section: {}'.format(heading))
                        current_section = Config.ConfigSection(heading=heading)
                        self[heading] = current_section
                    continue

                if not current_section:
                    continue

                line_split = line.find(':')
                if line_split == -1:
                    continue

                option = line[:line_split].strip()
                value = line[line_split + 1:].strip()

                if ',' in line:
                    # an array value
                    value = value.split(',')
                    result = list()
                    for element in value:
                        element = element.strip()
                        if not element:
                            continue
                        result.append(element)
                    value = result

                current_value = current_section[option]
                if current_value != value:
                    Config.logger.debug('Updating configuration option: {} with value: {}'.format(value, option))
                    current_section[option] = value

    def __init__(self, config_file=None):
        Config.logger.debug('Config instance: {} Config file: {}'.format(Config._instance, config_file))
        if config_file and not Config._instance:
            Config._instance = Config.ConfigInstance(config_file)
        elif config_file:
            Config._instance.load_config(config_file)
        elif Config._instance is None:
            raise ValueError('No configuration instance specified. Config file must be given')

    def __setattr__(self, key, value):
        setattr(Config._instance, key, value)

    def __getattr__(self, item):
        return getattr(Config._instance, item)

