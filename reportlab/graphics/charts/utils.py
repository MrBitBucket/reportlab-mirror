"Utilities used here and there."

from time import mktime, gmtime, strftime
from math import log10
import string


def mkTimeTuple(timeString):
    "Convert a 'dd/mm/yyyy' formatted string to a tuple for use in the time module."

    list = [0] * 9
    dd, mm, yyyy = map(int, string.split(timeString, '/'))
    list[:3] = [yyyy, mm, dd]
    
    return tuple(list)


def str2seconds(timeString):
    "Convert a number of seconds since the epoch into a date string."

    return mktime(mkTimeTuple(timeString))


def seconds2str(seconds):
    "Convert a date string into the number of seconds since the epoch."

    return strftime('%Y-%m-%d', gmtime(seconds))


def nextRoundNumber(x):
    """Return the first 'nice round number' greater than or equal to x

    Used in selecting apropriate tick mark intervals; we say we want
    an interval which places ticks at least 10 points apart, work out
    what that is in chart space, and ask for the nextRoundNumber().
    Tries the series 1,2,5,10,20,50,100.., going up or down as needed.
    """
    
    #guess to nearest order of magnitude
    if x in (0, 1):
        return x

    if x < 0:
        return -1.0 * nextRoundNumber(-x)
    else:
        lg = int(log10(x))

        if lg == 0:
            if x < 1:
                base = 0.1
            else:
                base = 1.0
        elif lg < 0:
            base = 10.0 ** (lg - 1)
        else:
            base = 10.0 ** lg    # e.g. base(153) = 100
        # base will always be lower than x

        if base >= x:
            return base * 1.0
        elif (base * 2) >= x:
            return base * 2.0
        elif (base * 5) >= x:
            return base * 5.0
        else:
            return base * 10.0
