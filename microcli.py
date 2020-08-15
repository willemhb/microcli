from functools import wraps, singledispatchmethod
import getopt as go
import re
from re import RegexFlag, Pattern
import sys, os
from inspect import signature, Parameter, _empty
from typing import Callable, Optional


""" This module provides a decorator that translates type hints and a formatted docstring into
    a command line interface. The intent is to provide an easier-to-use and more intuitive 
    (though less powerful) alternative to the argparse module.
"""

# Global constants
EMPTY = _empty
ARGDOC_PAT = re.compile(r"(\w+): (.+[!.?]\n?)")  # This regular expression helps extract parts of the docstring to use in
                                                 # the cli help message.


def cliargdocs(doc: str) -> str:
    """ Get the section of the docstring corresponding to arguments.
        return it to process and use in a command line help string.
    """

    try:
        start = doc.index("Args:") + 5
        end = doc.index("\n\n")

        return doc[start:end]

    except ValueError:
        return ""


def pstocls(p: str) -> str:
    """ Convert a string from Python style (words separated by '_')
        to cli style (words separated by '-').
    """
    return p.replace("_", "-")


def hdoc(w: int) -> str:
    """ Produce documentation for the '-h'/'--help' command.
    """
    hcommand = "-h, --help".rjust(w)
    hmsg = "view this help message.\n"

    return f"    {hcommand} : {hmsg}"


def parseargdocs(argdoc: str) -> list:
    """ Convert a blob of argument documentation into a list of command line documentation.
    """

    matches = []

    for m in re.finditer(ARGDOC_PAT, argdoc):
        matches.append(m.groups())

    else:
        matches[-1] += "\n\n"

        return matches


def formatargdocs(argdoc: list) -> str:
    """ Produce a final formatted string for use in command line documentation.
    """
    argdoc = argdoc[:]  # make a copy in case we want to use this elsewhere
    width = max(len(m[0]) for m in list) + 6  # get the width of the longest argument name
                                              # for formatting.

    for i, m in argdoc:
        a, h = m
        asx = f"-{a[0]}, --{pstocls(a)}"
        argdoc[i] = f"    {asx:{width}} : {h}"

    return "Optional Arguments:\n\n" + hdoc(width) + "".join(argdoc)


def pytocli(p: str, required: bool) -> tuple:
    """ Convert parameter from Python style (words separated by '_')
        to cli style (words separated by '-').
    """
    sopt = f"{p[0]}{':' if required else ''}"
    lopt = f"{p.replace('_', '-')}{'=' if required else ''}"

    return sopt, lopt


class PyCLIParameter(Parameter):
    """ This extension to the inspect.Parameter class holds a string matching
    the cli form of an argument.
    """
    empty = EMPTY
    POSITIONAL_ONLY = Parameter.POSITIONAL_ONLY
    POSITIONAL_OR_KEYWORD = Parameter.POSITIONAL_ONLY
    VAR_POSITIONAL = Parameter.VAR_POSITIONAL
    KEYWORD_ONLY = Parameter.KEYWORD_ONLY
    VAR_KEYWORD = Parameter.VAR_KEYWORD

    @singledispatchmethod
    def __init__(self, name: str, kind, *, default=EMPTY, annotation=EMPTY):
        """ Default constructor passes all arguments to super constructor
            and then finds the cli-name(s) that matches this argument,
            storing these in shortopt and longopt.
        """
        super().__init__(name, kind, default, annotation)

        if kind not in self.VAR_ARGS:
            so, lo = pytocli(self.name, default is EMPTY)

        else:
            so, lo = None, None

        self.shortopt = so
        self.longopt = lo

    @__init__.register
    def _(self, p: Parameter):
        """ Pass the attributes of p to the default constructor.
        """
        self.__init__(p.name, p.kind, default=p.default, annotation=p.annotation)

    @property
    def annotation_name(self):
        """ Simple helper for getting the name of the class of the annotation.
        """
        return '' if self.annotation is EMPTY else self.annotation.__name__

    def __str__(self):
        """ Patterned after str(Parameter), but includes the cli string.
        """
        fmt = """<PyCLIParameter "{}{}{}{}">""".format
        n = self.name
        t = '' if self.annotation is EMPTY else f" : {self.annotation_name}"
        d = '' if self.default is EMPTY else f" = {self.default}"
        c = '' if not self.shortopt else f" ({self.shortopt}, {self.longopt})"

        return fmt(n, t, d, c)


class CLIArgs(dict):
    """This dict subclass holds the PyCLIParameters for a function."""
    __slots__ = ()

    def __init__(self, func: Callable):
        """ Call this directly on a callable; add keys to self in the order they
            appear in the Signature.parameters mappingproxy.
        """
        try:
            parms = signature(func).parameters

            for k in parms:
                self[k] = PyCLIParameter(parms[k])

        except (TypeError, ValueError):
            raise NotImplementedError

    @property
    def orderedargs(self):
        """ Return an iterator over the keys in self whose kind is not
            KEYWORD_ONLY or VAR_KEYWORD. Each item in the iterator returns the 
            argcount.
        """
        def generator(d):
            for k in d:
                arg = d[k]

                if arg.kind == arg.POSITIONAL_ONLY or arg.kind == arg.VAR_POSITIONAL:
                    yield k

        return enumerate(generator(self), start=1)

    @property
    def shortoptstr(self):
        """ Return a string of all the short options, suitable for use in getopt.
        """
        return "".join(p.shortopt for p in self.values())

    @property
    def longoptlist(self):
        """ Return a list of the long options, suitable for use in getopt."""

    def __str__(self):
        """ String method displays type."""
        pairs = []

        for k in self:
            pairs.append(f"[{k}, {self[k]}]")

        return f"CLIArgs({', '.join(pairs)})"


def makeusage(args: CLIArgs) -> Callable:
    """ Create and return a function to describe correct usage
        of the application to the user.
    """
    pass


def cliparse(params: CLIArgs):
    pass


def microcli(app):
    docs = ""
    @wraps(app)
    def inner(*args, **kwargs):
        if "-h" in args or "--help" in args:
            print(docs)
            exit(0)

        else:
            return app(*args, **kwargs)

    return inner
