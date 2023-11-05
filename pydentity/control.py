from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydentity import Contract


class Control(object):
    def __init__(self, engine: str, dsn: str = None):
        self._contracts = []
    
    @staticmethod
    def _evaluate(conditions: dict):
        # check if dict key starts with ? or &
        for key in conditions:
            char = key[0]
            {'?': 'OR', '&': 'AND'}.get(char)
    
    def add(self, *contracts: 'Contract'):
        for contract in contracts:
            if not contract._on:
                raise ValueError('Every contract must have a valid action and destination before being added to a control')
            for action in contract._on:
                payload = contract._payload
                payload['on'] = action
                self._contracts.append(payload)

    def save(self):
        pass
    
    def contact(self, contact: dict):
        return self
    
    def content(self, content: dict):
        return self
    
    def context(self, context: dict):
        return self
    
    @property
    def start(self):
        return Guard(self)


class Guard(object):
    def __init__(self, control: Control):
        self._control = control

    def on(self, action: str):
        return self
    
    def to(self, destination: str):
        return self
    
    @property
    def accepts(self) -> bool:
        return False
    
    @property
    def rejects(self) -> bool:
        return True
