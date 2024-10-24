
from typing import TYPE_CHECKING

from pidentity.constants import SYMBOLS, OPERANDS


if TYPE_CHECKING:
    from pidentity import Control


class Guard(object):
    def __init__(self, control: 'Control'):
        self._contact = None
        self._content = None
        self._context = None
        self._control = control
        self._contract = None

    @staticmethod
    def _parse(k: str, v: any):
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

    def _evaluator(self, conditions: dict, data: dict):
        """
        Evaluate the conditions i.e. {
            '&id:==': '132313122',
            '&name:==': 'John Doe',
            '&age:==': 18,
            '&location@==': 'context.location',
            '&reference@??': 'contact.id',
            '&address:::': {
                '&city:==': 'New York',
                '&state:==': 'NY',
            }
        }
        
        1. get the key so we can expand it
            - &id:== will be expanded into key, op where op is <type, equals: Callable> and key = &id
            the key &reference@?? will be op <type, Callable: refs('contact.id', op: Callable)>
        
        2. extract the values from the data to run the ops upon

        # Content Evaluation
        {
            '@': lambda (k: string): return 
            ':': lambda k: 
        }
            
        """
        def _exparse(k: str):
            # &location@== -> &, location, @==
            return k[0], k[1:-3], k[-3:]

        for token, scale in conditions.items():
            prefix, key, op = _exparse(token)
            value = data.get(key)
            Operation(op).compare(value, scale)
    
    def _operation(self):
        pass

    def _opspand(self, op: str):
        if op.startswith('@'): return {}
        return {}

    def contact(self, data: dict) -> 'Guard':
        return self
    
    def content(self, data: dict) -> 'Guard':
        return self

    def context(self, data: dict) -> 'Guard':
        return self

    def contact(self, contact: dict) -> 'Guard':
        return self

    async def resync(self):...

    def resyncs():
        pass

    async def scan(self) -> bool:
        return True

    def scans(self):
        return True

    def on(self, action: str):
        return self

    def to(self, resource: str):
        return self
