""" This handles the parsing of command line arguments.
"""
import sys
import re
from util import Void
import micro_inspect as mui
from typing import Callable, Union, Tuple


# Regexes for parsing command-line options
shflag_p = re.compile(r"^-([a-zA-Z])")
lflag_p = re.compile(r"^--([a-zA-Z][-a-zA-Z]+)")
sharg_p = re.compile(r"^-([a-zA-Z]):(.+)")
larg_p = re.compile(r"^--([a-zA-Z][-a-zA-Z]+)=(.+)")

# Global constants
Unknown = Void.UNKNOWN
Undefined = Void.UNDEFINED
Nil = Void.NIL


def clitopy(arg: str) -> str:
    # change a string from cli style (words separated by '-')
    # to Python style (words separated by '_')
    return arg.replace("-", "_")


def parsearg(arg: str) -> tuple:
    # Try to parse the argument using the regexes above
    # If all regexes fail, return a tuple whose first element
    # is None, signifying no match
    if (m := shflag_p.match(arg) or lflag_p.match(arg)):
        return m[1], True

    elif (m := sharg_p.match(arg) or larg_p.match(arg)):
        return m.groups()

    else:
        return None, arg 


def parseargs(argv: list) -> tuple:
    # parse the list of command line arguments and return a tuple of
    # positional and keyword arguments (the list argv is assumed to be
    # the raw sys.argv, so we'll strip the first argument.)
    positionals = []
    options = {}
    args = iter(argv)
    next(args)

    for arg in args:
        arg, val = parsearg(arg)

        if arg is None:
            positionals.append(val)

        else:
            options[clitopy(arg)] = val

    return positionals, options
