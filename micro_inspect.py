""" This module provides much of the functionality of the inspect module
    in a smaller, simpler API.
"""


from inspect import CO_VARARGS, CO_VARKEYWORDS
from typing import Callable, Union, Any
from util import Void
from enum import Flag, auto


class ArgKind(Flag):
    """ Flag holds information on the argument kind.
    """
    POSARG = auto()
    KWARG = auto()
    VARG = auto()
    VARKW = auto()
    AMBARG = POSARG | KWARG

    def __str__(self):
        # Return the name of the instance, title-cased
        return f"{self.name.title()}({self.value})"


# Global constants
Code = (lambda x: x).__code__.__class__
Unknown = Void.UNKNOWN
Undefined = Void.UNDEFINED
Nil = Void.NIL
PosArg = ArgKind.POSARG
KwArg = ArgKind.KWARG
Varg = ArgKind.VARG
VarKw = ArgKind.VARKW
AmbArg = ArgKind.AMBARG


# Get code and flags objects
def getcode(fun: Callable) -> Code:
    # return this function's code object
    return fun.__code__


def getflags(fun: Callable) -> int:
    # get this function's flags
    return fun.__code__.co_flags


# Check for vararg arguments
def hasvargs(fun: Callable) -> bool:
    # determine if this function has *args
    return bool(fun.__code__.co_flags & CO_VARARGS)


def hasvarkw(fun: Callable) -> bool:
    # determine if this function has **kwargs
    return bool(fun.__code__.co_flags & CO_VARKEYWORDS)


# Get argument counts, broken down by argument kind
def posxargco(fun: Callable) -> int:
    # get this function's count of positional only arguments
    return fun.__code__.co_posonlyargcount


def posargco(fun: Callable) -> int:
    # get this function's count of all arguments that can be called positionally
    return fun.__code__.co_argcount


def ambargco(fun: Callable) -> int:
    # Get this function's count of all arguments that can be called positionally or by name
    co = fun.__code__

    return co.co_argcount - co.co_posonlyargcount


def kwxargco(fun: Callable) -> int:
    # get this function's count of keyword-only argument
    return fun.__code__.co_kwonlyargcount


def kwargco(fun: Callable) -> int:
    # get this function's count of all functions that can be called by name
    co = fun.__code__

    return co.co_kwonlyargcount + co.co_argcount - co.co_posonlyargcount


def argco(fun: Callable) -> int:
    # get the full count of this function's argument
    co = fun.__code__

    return co.co_argcount + co.co_kwonlyargcount


# Get arguments, broken down by argument kinds
def posargs(fun: Callable) -> tuple:
    # get a list of this function's positional arguments
    return fun.__code__.co_varnames[:fun.__code__.co_argcount]


def posxargs(fun: Callable) -> tuple:
    # get a list of this function's positional only arguments
    return fun.__code__.co_varnames[:fun.__code__.co_posonlyargcount]


def ambargs(fun: Callable) -> tuple:
    # get a list of this functions ambargs
    posargs_i = fun.__code__.co_posonlyargcount
    ambargs_i = fun.__code__.co_argcount
    return fun.__code__.co_varnames[posargs_i:ambargs_i]


def kwargs(fun: Callable) -> tuple:
    # get a list of this function's keyword arguments
    co = fun.__code__
    start_i = co.co_posonlyargcount
    stop_i = co.co_argcount + co.co_kwonlyargcount
    return co.co_varnames[start_i:stop_i]


def kwxargs(fun: Callable) -> tuple:
    # get a list of this function's keyword-only arguments
    co = fun.__code__
    start_i = co.co_argcount
    stop_i = start_i + co.co_kwonlyargcount
    return co.co_varnames[start_i:stop_i]


def funargs(fun: Callable) -> tuple:
    # Get a list of all of this function's non varargs
    co = fun.__code__
    stop_i = co.co_argcount + co.co_kwonlyargcount
    return co.co_varnames[:stop_i]


def vfunargs(fun: Callable) -> tuple:
    # Get a list of all arguments, including vargs and varkw
    co = fun.__code__
    stop_i = co.co_argcount + co.co_kwonlyargcount + hasvargs(fun) + hasvarkw(fun)
    return co.co_varnames[:stop_i]


# Get type and kind annotations.
def argtypes(fun: Callable) -> dict:
    # functional wrapper for annotations, sans-return type
    t = {a: Unknown for a in funargs(fun)}
    annotations = fun.__annotations__

    for a in annotations:
        t[a] = annotations[a]

    return t


def returntype(fun: Callable) -> Union[Void, type]:
    # check for a return type in the function's signature and return it if it exists
    if "return" in (a := fun.__annotations__):
        return a["return"]

    return Unknown


def argkinds(fun: Callable) -> dict:
    # Get a tuple of the argument kinds
    argnames = vfunargs(fun)
    argkinds = [PosArg] * posxargco(fun) + [AmbArg] * ambargco(fun) + [KwArg]

    if hasvargs(fun):
        argkinds.append(Varg)

    if hasvarkw(fun):
        argkinds.append(VarKw)

    return argkinds


def argdefaults(fun: Callable) -> dict:
    # Get a mapping of the default arguments for this function
    co = fun.__code__
    names = funargs(fun)
    d = {a: Undefined for a in names}

    if (kd := fun.__kwdefaults__):
        d.update(kd)

    if (od := fun.__defaults__):
        stop_i = co.co_argcount
        start_i = stop_i - len(od)
        dnames = names[start_i:stop_i]

        for i, dn in enumerate(dnames):
            d[dn] = od[i]

    return d


# These functions produce argument information for other functions
# to query or try to match against
def getfullargspec(fun: Callable) -> dict:
    # Return a dictionary containing a full argument spec for fun - names,
    # kinds, types, return type, and defaults
    output = {}

    output["names"] = vfunargs(fun)
    output["defaults"] = argdefaults(fun)
    output["kinds"] = argkinds(fun)
    output["types"] = argtypes(fun)
    output["return"] = returntype(fun)
    output["posxargco"] = posxargco(fun)
    output["ambargco"] = ambargco(fun)
    output["kwxargco"] = kwxargco(fun)
    output["hasvargs"] = hasvargs(fun)
    output["hasvarkw"] = hasvarkw(fun)

    return output


def makeargtemplate(fun: Callable, argspec=False, /) -> tuple:
    # Return a template for this function for processes that want
    # to call the function to attempt to fill in with actual values.
    # if argspec is True, include an argspec in the return tuple
    positionals = []
    kwargs = {}
    defaults = argdefaults(fun)

    if argspec:
        return positionals, kwargs, defaults, getfullargspec(fun)

    return positionals, kwargs, defaults
