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

    @wraps(app)
    def wrapper(argv):
        """ sys.argv should be passed to this wrapper directly. It will handle removing
            the script name from sys.argv.
        """
        argl = argv[1:]

        if "-h" in argl or "--help" in argl:
            print(app.__doc__)
            quit(0)

        debug = "-d" in argl or "--debug" in argl
        argspec = mui.getfullargspec(app)
        pos, opt = cli_p.parseargs(argl)

        if debug:
            print("Initial parse successful.")
            print(f"Parsed positional arguments: {pos}")
            print(f"Parsed options: {opt}")
            print(f"argspec: {argspec}")

        m_pos, m_opt = cli_p.matchargs(pos, opt, argspec)

        if m_pos is None:
            if debug:
                print(f"Match error: {m_opt}")
                exit(1)

        if debug:
            print("Secondary parse successful.")
            print(f"Matched positional arguments: {m_pos}")
            print(f"Matched options: {m_opt}")

        try:
            return app(*m_pos, **m_opt)

        except Exception as e:
            if debug:
                raise e

            else:
                print("Fatal exception.")
                exit(1)

    return wrapper
