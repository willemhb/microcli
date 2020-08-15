from functools import wraps
import re
import sys, os
from typing import Optional, Union, Tuple
from inspect import signature, Signature, Parameter, BoundArguments, _empty
from collections import namedtuple


""" This module provides a decorator that translates type hints and a formatted docstring into
    a command line interface. The intent is to provide an easier-to-use and more intuitive 
    (though less powerful) alternative to the argparse module.
"""

# Convenience bindings for argument kinds
POS_ARG = Parameter.POSITIONAL_ONLY
KW_ARG = Parameter.KEYWORD_ONLY
POS_OR_KW_ARG = Parameter.POSITIONAL_OR_KEYWORD
POS_VARG = Parameter.VAR_POSITIONAL
KW_VARG = Parameter.VAR_KEYWORD
Empty = _empty


# Helpers for working with parameters and signatures
def required(p: Parameter) -> bool:
    """ Test whether the parameter has a default value.
    """
    return p.default is Empty


#  Helpers for working with function signatures
def argco(s: Signature) -> int:
    """ Return the length of the parameters dict.
    """
    return len(s.parameters)


def posargco(s: Signature) -> int:
    """ Return the number of parameters in dict whose
        kind is positional only.
    """
    return sum(p.kind == POS_ARG for p in s.parameters)


def kwargco(s: Signature) -> int:
    """ Return the number of parameters in dict whose
        kind is keyword only.
    """
    return sum(p.kind == KW_ARG for p in s.parameters)


def kwposargco(s: Signature) -> int:
    """ Return the number of parameters in dict whose
        kind is keyword or positional only.
    """
    return sum(p.kind == POS_OR_KW_ARG for p in s.parameters)


ArgcoSpec = namedtuple("ArgcoSpec", ["pos", "kw", "pos_kw", "var_pos", "var_kw"])


def argcospec(s: Signature) -> ArgcoSpec:
    """ Return a full description of the argument counts for the given signature.
    """
    acd = [0] * 5
    
    for p in s.parameters.values:
        if (k := pspec.kind) == POS_ARG:
            acd[0] += 1

        elif k == KW_ARG:
            acd[1] += 1

        elif k == POS_OR_KW_ARG:
            acd[2] += 1

        elif k == VAR_POS:
            acd[3] += 1

        else:
            acd[4] += 1

    return ArgcoSpec._make(acd)


# Parsing helpers
shortopt = re.compile(r"^-([a-zA-Z])")
longopt = re.compile(r"^--([a-zA-Z][-a-zA-Z]+)")
longarg = re.compile(r"^--([a-zA-Z][-a-zA-Z]+)=(.+)")


def parseopt(opt: str) -> tuple:
    """ Try to parse the string using the shortopt, longopt, and longarg regular expressions.
        if a pattern matches, return a tuple of all match groups with the argument or flag 
        transformed from CLI to Python style. Otherwise, return a tuple whose first element is
        the empty string and whose second element is the unchanged option.
        
    """
    if (m := shortopt.match(opt) or longopt.fullmatch(op)):
        arg = m[1]

        return arg.replace("-", "_"), True  # Interpret flags as booleans

    elif (m := longarg.match(opt)):
        arg, argv = m.groups()

        return arg.replace("-", "_"), argv
    
    return "", opt


# Exception classes
class UnknownOptionError(RuntimeError):
    pass

class UnknownFlagError(RuntimeError):
    pass

class CLIArityError(RuntimeError):
    pass





def parseargv(s: Signature) -> Tuple[tuple, dict]:
    """ Do an initial parse of the command line arguments, attempting
        to return a tuple and a dict that can be used with Signature.bind.
        Raise an error if the command line arguments can't be interpreted in a way
        consistent with the function signature.
    """
    sys_argv = sys.argv[1:]
    fun_args = dict(s.parameters)
    pos, kw, pos_kw, var_pos, var_kw = argcospec(s)
    bound_pos = []
    bound_vpos = []
    bound_kw = {}
    bound_vkw = {}


    for arg, argv in map(parseopt, argv):
        if arg == "":  # Failed to match a flag, try to interpret it as a positional argument
            if pos:    # If positional arguments haven't been used up
                bound_pos.append(argv)
                pos -= 1

            elif var_pos:
                bound_vpos.append(argv)

            else:
                raise CLIArityError("Too many arguments supplied.")

        elif len(arg) == 1:
            pass

        else:
            pass
            


def microcli(app):
    @wraps(app)
    def inner(*args, **kwargs):
        cliargs = sys.argv[1:]
        if "-h" in args or "--help" in args:
            print(app.__doc__)
            exit(0)

        else:
            return app(*args, **kwargs)

    return inner
