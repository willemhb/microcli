""" This handles the parsing of command line arguments.
"""
import sys
import re
from util import Void
import micro_inspect as mui
from typing import Callable, Union, Tuple
from itertools import takewhile


# Regexes for parsing command-line options
shflag_p = re.compile(r"^-([a-zA-Z])")
lflag_p = re.compile(r"^--([a-zA-Z][-a-zA-Z]+)")
sharg_p = re.compile(r"^-([a-zA-Z]):(.+)")
larg_p = re.compile(r"^--([a-zA-Z][-a-zA-Z]+)=(.+)")

# Global constants
Unknown = Void.UNKNOWN
Undefined = Void.UNDEFINED
Nil = Void.NIL
COMMON_FLAGS = {"d", "debug", "h", "help"}


def parsearg(arg: str) -> tuple:
    # Try to parse the argument using the regexes above
    # If all regexes fail, return a tuple whose first element
    # is None, signifying no match
    if (m := shflag_p.match(arg) or lflag_p.match(arg)):
        return m[1].replace("-", "_"), True

    elif (m := sharg_p.match(arg) or larg_p.match(arg)):
        opt, val = m.groups()
        return opt.replace("-", "_"), val

    else:
        return None, arg


def parseargs(argv: list) -> tuple:
    # parse the list of command line arguments and return a tuple of
    # positional and keyword arguments (the list argv is assumed to be
    # the raw sys.argv, so we'll strip the first argument.)
    positionals = []
    options = {}

    for arg in argv:
        arg, val = parsearg(arg)

        if arg is None:
            positionals.append(val)

        else:
            options[arg] = val

    return positionals, options


def matchargs(positionals: list, options: dict, argspec: dict) -> tuple:
    """ Check that the function that produced argspec can be called with the supplied
        positionals and options. If it can, return a tuple of positionals and keyword
        arguments ready to be called (fun(*t[0], **t[1])). Otherwise, return an empty
        tuple.
    """
    # create containers for the matched arguments
    p_out = []
    kw_out = {}
    va_out = [] if argspec["hasvargs"] else None


    npos_given = len(positionals)
    nkw_given = len(options)

    hasvargs = argspec["hasvargs"]
    hasvarkw = argspec["hasvarkw"]
    names = argspec["names"]
    posxnames = argspec["posxnames"]
    kwxnames = argspec["kwxnames"]
    ambnames = argspec["ambnames"]
    ambco = argspec["ambargco"]
    defaults = argspec["defaults"]
    minpos = sum(k == mui.PosArg and d == Undefined for _, _, d, k, _ in mui.iterargspec(argspec))
    maxpos = ambco + minpos
    minkw = sum(k == mui.KwArg and d == Undefined for _, _, d, k, _ in mui.iterargspec(argspec))
    maxkw = minkw + ambco

    if npos_given < minpos or nkw_given < minkw:
        return None, "insufficient arguments"


    if npos_given > maxpos and not hasvargs or nkw_given > maxkw and not hasvarkw:
        return None, "too many arguments"

    # ASSERT: the number of arguments is consistent with the spec
    unmatched = list(names[:-1*(hasvargs + hasvarkw)])
    posnames = list(reversed(posxnames + ambnames))
    positionals.reverse()

    while positionals and posnames:
        p_out.append(positionals.pop())
        unmatched.remove(posnames.pop())

    if positionals:
        if hasvargs:
            p_out.extend(reversed(positionals))

        else:
            return None, "too many positionals"

    if posnames:
        for p in posnames:
            if defaults[p] is Undefined:
                return None, f"missing default for {p}"

            else:
                p_out.append(defaults[p])
                unmatched.remove(p)

    # ASSERT: All positionals have been matched
    # Next, attempt to match the options
    for o in options:
        if o in COMMON_FLAGS:
            kw_out[o] = options[o]

        if o in unmatched:
            kw_out[o] = options[o]
            unmatched.remove(o)

        elif len((m := [u for u in unmatched if u.startswith(o)])) == 1:
            try:
                mo = m[0]
                kw_out[mo] = options[o]
                unmatched.remove(mo)

            except ValueError as e:
                print(f"Tried to remove non-matching option {mo}.")
                raise e

        elif hasvarkw:
            kw_out[o] = options[o]

        else:
            return None, f"Couldn't find unambiguos match for option {o}"
            
    for u in unmatched:
        if defaults[u] is Undefined:
            return None, f"Couldn't match all: {unmatched}"

        else:
            kw_out[u] = defaults[u]

    # ASSERT: All keyword arguments have been matched and all options have matched a keyword
    # argument
    return p_out, kw_out  # success!
