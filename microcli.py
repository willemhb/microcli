""" This module provides a decorator that translates type hints and a formatted docstring into
    a command line interface. The intent is to provide an easier-to-use and more intuitive 
    (though less powerful) alternative to the argparse module.
"""
import sys
import micro_inspect as mui
import cliparse as cli_p
from functools import wraps


def microcli(app):
    """ This decorator implements the microcli interface -- wrapping an application in
        with the microcli decorator will parse arguments from the command line
        and attempt to match them to arguments in the wrapped function using its
        argspec.
    """
    ARGSPEC = mui.getargspec(app)

    @wraps(app)
    def inner(*args, **kwargs):
        template = {**ARGSPEC["defaults"]}
        args = cli_p.parseargs(sys.argv)

        positionals, 

    return inner
