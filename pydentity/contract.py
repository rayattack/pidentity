from pydentity.constants import CONTACT, CONTENT, CONTEXT, MACROS, OPERANDS, SYMBOLS
from pydentity.operators import EQ
from pydentity.rules import Ref, Rule



class Contract(object):
    """
    Contract is a policy builder AND is saved verbatim with no processing done, only validation
    of condition syntax as the actual matching and processing is done in the controls when this
    contract is retrieved from the chosen data store.
    """
    def __init__(self, domain: str):
        self._on = []
        self._payload = {
            'on': '',  # will be saved as single actions with to, contact, content, context etc. copied to each action
            'to': '',
            'domain': domain,
            CONTACT: {},
            CONTENT: {},
            CONTEXT: {},
        }

    @staticmethod
    def prepare(data: dict, macros=False):
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
            if macros and not macro:
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

            print('this is the val: ', val)
            return f'{k}{suffix}', val

        _data = {}
        for key, value in data.items():
            k, v = _(key, value)
            _data[k] = v
        return _data

    def on(self, *actions: str):
        """If you want this contract to apply to multiple actions, you can pass them in here
        otherwise pass in single action to the to method.
        Irrespective of how many actions you pass in here, the contract will be saved as a single
        policy with the content, context, contact data copied to each saved action.
        """
        self._on = actions
        return self

    def to(self, target: str):
        self._payload['to'] = target
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
