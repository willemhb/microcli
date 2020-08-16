""" Utilities and helpers for microcli.
"""
from enum import Enum


class Void(Enum):
    """ This Enum represents values that haven't been supplied. It is intended
        to provide more information None, while also being distinct from None
        (this makes it useful for introspecting and metaprogramming, where None
        could be a regular Python value and is therefore unsuited to flagging
        missing information).
    """
    UNKNOWN = 1
    UNDEFINED = 2
    NIL = 3

    def __bool__(self):
        # Like None, Void values are falsy
        return False

    def __str__(self):
        # Return a title-cased version of the instance's name
        return f"{self.name.title()}-({self.value})"

