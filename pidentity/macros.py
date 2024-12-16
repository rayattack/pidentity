from datetime import datetime, date, timedelta


# this is a placeholder until we get the comparator functions all defined
def placeholder(*args, **kwargs):...


# this evaluates two values are equal
def equals(a, b, coerce = False):
    if(coerce):
        typ = type(b)
        try: a = typ(a)
        except: return False
    else:
        if not isinstance(a, type(b)): return False
    return a == b


OPERATIONS = {
    ':==': equals
}


class Operation(object):
    def __init__(self, symbol: str, value: any, reference: bool = None):
        self.__symbol = symbol
        self.__value = value
        self.reference = reference

    def evaluate(self):
        pass

