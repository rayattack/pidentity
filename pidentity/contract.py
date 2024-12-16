from pidentity.constants import CONTACT, CONTENT, CONTEXT, DOMAIN, MACROS, OPERANDS, SYMBOLS, ON, TO, AT
from pidentity.database import SELECT_CONDITIONS_SQL
from pidentity.operators import EQ
from pidentity.rules import Ref, Rule

from typing import TYPE_CHECKING
if TYPE_CHECKING: from pidentity.control import Control


class Contract(object):
    """
    Contract is a policy builder AND is saved verbatim with no processing done, only validation
    of condition syntax as the actual matching and processing is done in the controls when this
    contract is retrieved from the chosen data store.
    """
    def __init__(self, domain: str = '*'):
        self._on = []  # iterate over this and repeat _payload with each as 'on' value
        self._payload = {
            'on': '',  # will be saved as single action with to, contact, content, context etc. copied to each action
            'to': '',
            DOMAIN: domain,
            CONTACT: {},
            CONTENT: {},
            CONTEXT: {},
        }

    def __view(self, on, to, at):
        cursor = self.cursor
        cursor.execute(SELECT_CONDITIONS_SQL, {ON: on, TO: to, AT: at})

    @staticmethod
    def prepare(data: dict, macros=False, expand = True):
        """Prepare the data for storage in the data store"""
        def _(k: str, v: any):
            if not k: raise ValueError('Invalid key')

            # with early exit out of the way let's get to work
            sym = k[0]
            ops = k[-3:]
            prefix = SYMBOLS.get(sym)
            suffix = OPERANDS.get(ops)

            # to prioritize the val provided suffix we need
            # to deprioritize the key: str provided suffix by removing it
            if(suffix): k = k[:-3]
            if(not prefix): k = f'&{k}'

            # at this point we are sure k has a prefix either added or provided
            macro = MACROS.get(k[1:])
            if macros and not macro:  # i.e. only runs in context cases where macros is True
                raise ValueError('Context keys must be macros')

            if isinstance(v, Rule):
                suffix = v.operator
                val = v.value
            elif isinstance(v, dict):
                suffix = ':::'
                val = Contract.prepare(v)
            else:
                _v = EQ(v)
                suffix = _v.operator
                val = _v.value

            return f'{k}{suffix}', val

        _data = {}
        for key, value in data.items():
            k, v = _(key, value)
            _data[k] = v
        return _data

    def at(self, op: str, data: dict) -> 'Contract':
        return self.what(op, data)

    def on(self, *actions: str):
        return self.upon(*actions)

    def to(self, target: str):
        return self.unto(target)

    def upon(self, *actions: str):
        """If you want this contract to apply to multiple actions, you can pass them in here
        otherwise pass in single action to the to method.
        Irrespective of how many actions you pass in here, the contract will be saved as a single
        policy with the content, context, contact data copied to each saved action.
        """
        self._on = actions
        return self

    def unto(self, target: str):
        self._payload['to'] = target
        return self

    def what(self, op, data: dict) -> 'Contract':
        if op not in [CONTACT, CONTENT, CONTEXT]:
            raise ValueError('Valid values for op: `contact`, `content`, `context`')
        self._payload[op.lower()] = Contract.prepare(data)
        return self

    def contact(self, contact: dict):
        self._payload[CONTACT] = Contract.prepare(contact)
        return self

    def context(self, context: dict):
        self._payload[CONTEXT] = Contract.prepare(context, macros=True)
        return self

    def content(self, content: dict):
        self._payload[CONTENT] = Contract.prepare(content)
        return self

    def this(self, key: str):
        # key must be of the order contact.key.more or context.key.more or content.key.or.more
        walkway = key.split('.')
        if walkway[0] not in ['contact', 'context', 'content']:
            raise ValueError(f'Invalid key {key}')
        return Ref(key)

