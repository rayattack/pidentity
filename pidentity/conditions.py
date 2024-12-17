from pidentity import Controller
from pidentity.constants import CONTACT, CONTENT, CONTEXT, DOMAIN, PIDENTITY, ON, TO, AT
from pidentity.macros import Operation, OPERATIONS

from typing import TYPE_CHECKING
if TYPE_CHECKING: from pidentity.control import Control


class Conditions(object):
    def __init__(self, ctrl: 'Control'):
        self.__ctrl = ctrl
        self.__at = ''
        self.__on = ''
        self.__to = ''
        self.__store = {}

    def __eval(self, what: str):
        contracts = self.__ctrl._contracts
        condition = contracts.get(f"{self.__on}:{self.__to}")
        if not condition: return None
        return condition.get(what)

    def on(self, on: str):
        self.__on = on
        return self

    def to(self, to: str):
        self.__to = to
        return self

    def at(self, at: str):
        self.__at = at
        return self

    def scan(self) -> dict:
        """This goes to the db if nothing exists in memory"""
        if not (self.__to and self.__at and self.__on):
            raise ValueError('Provide complete condition options to scan')
        condition = self.__eval(self.__at)
        if not condition: # time to go to db
            return self.__ctrl.select(self.__on, self.__to, self.__at)
        return condition

    def sync(self):
        """This syncs all content, contact, context into memory for evaluation"""
        for c in ['content', 'context', 'contact']:
            self.__at = c
            data = self.scan()
            self.__store[c] = data
        return self
    
    @property
    def control(self):
        return self.__ctrl

    @property
    def contact(self):
        cached = self.__store.get('contact')
        if cached: return cached
        return self.__eval(CONTACT)

    @property
    def content(self):
        cached = self.__store.get('content')
        if cached: return cached
        return self.__eval(CONTENT)

    @property
    def context(self):
        cached = self.__store.get('context')
        if cached: return cached
        return self.__eval(CONTEXT)

    def start(self):
        return Controller(self)

