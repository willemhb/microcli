from inspect import getargs
from enum import Enum, FlagEnum
from collections import namedtuple
from typing import Callable, Any

""" This module implements classes and functions to help with
    microcli.py. A lot of this stuff is a simpler version of more or less
    the same API provided by the inspect module.
"""



# Lol this is a dumb way to get the __class__ of a code object
Code = (lambda x: x).__code__.__class__



# Base class for a single argument spec

class VoidOption(Enum):
    """ Enum class representing argument spec information that was not supplied.
    """
    UNKNOWN = 1
    UNDEFINED = 2

    def __bool__(self):
        """ Always False."""
        return False

    def __str__(self):
        """ Return a title-cased str of just the name.
        """
        return self.name.title()


class ArgFlags(FlagEnum):
    """ Enum class representing an argument kind (similar to the one in inspect 
        module but simpler to use.
    """
    POS_ARG = auto()
    KW_ARG = auto()
    VARG = auot()
    POS_KW_ARG = POS_ARG | KW_ARG
    POS_VARG = POS_ARG | VARG
    KW_VARG = KW_ARG | VARG

    def __str__(self):
        """ Just the title-cased name.
        """
        return self.name.title()


# Introspection helpers
def funcode(func: Callable) -> Code:
    """ Get a function's code object.
    """
    return func.__code__


def posargco(func: Callable) -> int:
    """ Return the number of positional only arguments.
    """
    return funcode(func).co_posonlyargcount


def kwargco(func: Callable) -> int:
    """ Return the number of keyword only arguments.
    """
    return funcode(func).co_kwonlyargcount


def anyargco(func: Callable) -> int:
    """ Return the number of keyword or positional arguments.
    """
    return funcode(func).co_argcount


def argcounts(func: Callable) -> tuple:
    """ Return a tuple of the full argcounts of the function.
    """
    co = funcode(func)
    return co.co_posonlyargcount, co.co_argcount, co.co_kwonlyargcount


def argco(func: Callable) -> int:
    """ Return the full argcount of the function.
    """
    return sum(argcounts(func))


def argnames(func: Callable) -> tuple:
    """ Get the argument names of func as a tuple.
    """
    return funcode(func).co_varnames[:argco(func)]


def argkind(arg: str, args: tuple, argcounts: tuple) -> ArgKind:
    _args = iter(args)
    p, pkw, kw = argcounts

    for _ in range(p):
        if next(_args) == arg:
            return POS_ONLY

    for _ in range(pkw):
        if next(_args) == arg:
            return POS_OR_KW

    for _ in range(kw):
        if next(_args) == arg:
            return KW_ONLY

    raise ValueError(f"No arg named {arg} in {args}")


def argtypes(func: Callable) -> dict:
    """ Functional wrapper for __annotations__.
    """
    types = {n: UNKNOWN for n in argnames(func)}
    types.update(func.__annotations__)

    return types


def returntype(func: Callable) -> Any:
    """ get a function's return type (default to EmptyOption).
    """
    if "return" in (d := func.__annnotations__):
        return d["return"]

    return UNKOWN


def argdefaults(func: Callable) -> dict:
    """ Get a dictionary of argument defaults.
    """
    defaults = {}
    parms = signature(func).parameters

    for p in parms:
        if p.default is Empty:
            defaults[p] = UNDEFINED

        else:
            defaults[p] = p.default

    return defaults


def pargtocliarg(arg: str) -> str:
    """ Convert argument name from Python style to CLI style.
    """
    return arg.replace("_", "-")


def pargtocliargs(arg: str) -> tuple:
    """ Convert an argument name from Python style to short- and
        long CLI options.
    """
    return f"{arg[0]}", f"--{pargtocliarg(arg)}"


def fmtcliargs(opts: tuple, doc: str, width: int) -> str:
    """ Produce a formatted help string for a single argument.
    """
    so, lo = opts
    return f"    {so}, {lo:{width}} : {doc}"


_CLIArg = namedtuple("CLIArgSpec", ["opts", "kind", "type", "default", "doc"])


class CLIArg(_CLIArg):
    """ Adds convenience methods and properties.
    """
    __slots__ = ()

    @property
    def shortopt(self):
        """ Return the short cli name.
        """
        return self.opts[0]

    @property
    def longopt(self):
        """ Return the long cli name.
        """
        return self.opts[1]

    @property
    def annotated(self):
        """ Return whether the type annotation exists.
        """
        return self.type is not UNKNOWN

    @property
    def hasefault(self):
        """ Return whether a default value exists.
        """
        return self.default is not UNKNOWN


class CLIArgs(dict):
    """ A mapping of arguments to essential spec information.
    """

    
