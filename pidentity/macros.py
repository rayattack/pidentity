from datetime import datetime, date, timedelta


# this is a placeholder until we get the comparator functions all defined
def placeholder(*args, **kwargs):...


# this evaluates two values are equal
def _eq(a, b, coerce = False):
    if(coerce):
        typ = type(b)
        try: a = typ(a)
        except: return False
    else:
        if not isinstance(a, type(b)): return False
    return a == b

def _neq(a, b): return a != b

def _gt(val, base): return val > base

def _gte(val, base): return val >= base

def _lt(val, base): return val < base

def _lte(val, base): return val <= base

def _btw(val, base):
    low, high = base
    return (val > low) and (val < high)

def _in(val, base): return val in base

def _nin(val, base): return val not in base


OPERATIONS = {
    ':==': _eq,
    ':!=': _neq,
    ':>>': _gt,
    ':><': _btw,
    ':<<': _lt,
    ':??': _in,
    ':!!': _nin,
    '@==': _eq
}


class Operation(object):
    def __init__(self, symbol: str, value: any, reference: bool = None):
        self.__symbol = symbol
        self.__value = value
        self.reference = reference

    def evaluate(self):
        pass

