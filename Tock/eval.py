from widgets import *
from backdrops import *
from greetings import *


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

