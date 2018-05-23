import re
import collections

class DotDict(dict):
    def __init__(self, **kwargs):
        super(DotDict, self).__init__(**kwargs)

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


class Subscriber(object):
    def update(self, updated_key):
        pass


class Config(object):
    _instance = None

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
            print('notifiying subscribers...')
            for subscriber in self.subscribers:
                subscriber.update(key)

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
                        print('already exists: {} type: {}'.format(heading, type(self[heading])))
                        current_section = self[heading]
                    else:
                        current_section = Config.ConfigSection(heading=heading)
                        self[heading] = current_section
                    continue

                if not current_section:
                    print('did not have a section')
                    continue

                line_split = line.find(':')
                if line_split == -1:
                    print('invalid conditions')
                    continue

                option = line[:line_split].strip()
                value = line[line_split + 1:].strip()

                current_value = current_section[option]
                if current_value != value:
                    current_section[option] = value

    def __init__(self, config_file=None):
        print('Config instance: {} Config file: {}'.format(Config._instance, config_file))
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

