import re

ARGDOC_PAT = re.compile(r"(\w+):\s+(.+[!.?]\n)")  # This regular expression helps extract parts of the docstring to use in
                                                 # the cli help message.



def pstocls(p: str) -> str:
    """ Convert a string from Python style (words separated by '_')
        to cli style (words separated by '-').
    """
    return p.replace("_", "-")
                                                 

def parsedocs(doc: str) -> tuple:
    """ Parse a doc string into 
    """
    try:
        dochead, args = doc.split("Args:")
        cutoff = doc.index("\n\n") + 1

        return dochead, args[:cutoff]

    except ValueError:
        return ""


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
    
