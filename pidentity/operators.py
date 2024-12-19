from typing import Any, Iterable

from pidentity.rules import Ref, Rule


ITER_REF_MSG = 'value must be an Iterable or lookup reference'


def __OP(op: str, val: Any) -> Rule:
    if isinstance(val, dict):
        raise ValueError('Dictionary values can only be used as nested rules and not with operators')
    if isinstance(val, Ref):
        # if we want to indicate to rule that this is a reference so behave differently in evaluation
        op = op.replace(':', '@')
        val = val.key
    return Rule(op, val)


def BTW(start: Any, end: Any):
    return __OP(':><', [start, end])


def EQ(val: Any) -> Rule:
    return __OP(':==', val)


def GT(val: Any) -> Rule:
    return __OP(':>>', val)


def GTE(val: Any) -> Rule:
    return __OP(':>=', val)


def IX(val: Any) -> Rule:
    if not isinstance(val, (list, tuple, str, Ref)):
        raise ValueError(f'IN {ITER_REF_MSG}')
    return __OP(':<>', val)


def IN(val: Iterable[object]) -> Rule:
    if not isinstance(val, (list, tuple, str, Ref)):
        raise ValueError(f'IN {ITER_REF_MSG}')
    return __OP(':[]', val)


def LT(val: Any) -> Rule:
    return __OP(':<<', val)


def LTE(val: Any) -> Rule:
    return __OP(':<=', val)


def NEQ(val: Any) -> Rule:
    return __OP(':!=', val)


def NIN(val: Any) -> Rule:
    if not isinstance(val, (list, tuple, str, Ref)):
        raise ValueError(f'NIN {ITER_REF_MSG}')
    return __OP(':][', val)


def REGEX(val: Any) -> Rule:
    return __OP(':~~', val)



OPERATORS = {
    ':[]': IN
}
