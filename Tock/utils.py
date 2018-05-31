import logging

from datetime import datetime

from widgets import *
from backdrops import *
from greetings import *


def seconds_until(time_str):
    current_timestamp = datetime.now()
    date_formats = ['-I:%M %p', '%H:%M']
    parsed_time = None

    for d_format in date_formats:
        try:
            parsed_time = datetime.strptime(time_str, d_format)
        except ValueError:
            continue
        else:
            break

    if not parsed_time:
        return

    parsed_time = parsed_time.replace(year=current_timestamp.year, day=current_timestamp.day, month=current_timestamp.month)

    if current_timestamp > parsed_time:
        parsed_time = parsed_time.replace(day=(current_timestamp.day + 1))

    return (parsed_time - current_timestamp).total_seconds()


def eval_widg(widg_name):
    logger = logging.getLogger('tock')
    try:
        widg_class = eval(widg_name)
    except NameError:
        logger.exception('ERROR: Could not find class {}'.format(widg_name))
        return None
    else:
        if callable(widg_class):
            widget = widg_class()
        else:
            widget = widg_class

        return widget
