from os import environ
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydentity import Contract


from pydentity.database import initialize_sql


class Control(object):
    def __init__(self, engine: str, connection = None):
        self._contracts = []
        self._pool = connection

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
    
    def can(self, action: str) -> 'Guard':
        return Guard(self).on(action)

    async def init(self):
        async with self._pool.acquire() as conn:
            await initialize_sql(conn)

    def save(self):
        pass

    @property
    def start(self):
        return Guard(self)


class Guard(object):
    def __init__(self, control: Control):
        self._contact = None
        self._content = None
        self._context = None
        self._control = control

    def contact(self, contact: dict):
        self._contact = contact

    def content(self, content: dict):
        self._content = content

    def context(self, context: dict):
        self._context = context

    def go(self) -> bool:
        return False

    def rejects(self) -> bool:
        return True

    def on(self, action: str):
        return self

    def to(self, destination: str):
        return self
