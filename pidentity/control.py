from json import dumps, loads
from os import environ, path, remove as nuke
from pathlib import Path
from typing import TYPE_CHECKING
from sqlite3 import Cursor, connect, Connection

from pidentity import Contract
from pidentity.constants import CONTACT, CONTENT, CONTEXT, DOMAIN, PIDENTITY, ON, TO, AT
from pidentity.database import (
    DELETE_CONDITIONS_SQL,
    INSERT_CONDITIONS_SQL,
    UPDATE_CONDITIONS_SQL,
    SELECT_CONDITIONS_SQL,
    SQL
)
from pidentity.guard import Guard


ON_REQUIRED = 'Every contract must have a valid action and destination before being added to a control'



class Controller(object):
    def __init__(self, *args, **kwargs):
        pass

    def content(self, values: dict):
        return self

    def context(self, values: dict):
        return self

    def contact(self, values: dict):
        return self
    
    def go(self) -> bool:
        return False


class Conditions(object):
    def __init__(self, ctrl: 'Control'):
        self.__ctrl = ctrl

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
    
    @property
    def control(self):
        return self.__ctrl

    @property
    def contact(self):
        return self.__eval(CONTACT)

    @property
    def content(self):
        return self.__eval(CONTENT)

    @property
    def context(self):
        return self.__eval(CONTEXT)


class Control(object):
    def __init__(self, engine: str):
        self._contracts = {}  # ['post:@:/v1/customers/:id', 'get:@:/v1/customers/id']
        Path('.pidentity').mkdir(exist_ok=True)
        self.__db = connect(f'.pidentity/{engine}.db')
        self._unsaved = []
        self._unswapped = []

    @staticmethod
    def _evaluate(conditions: dict):
        # check if dict key starts with ? or &
        # TODO: remove if unused which appears to be the case
        for key in conditions:
            char = key[0]
            {'?': 'OR', '&': 'AND'}.get(char)

    def __save(self) -> 'Control':
        cursor = self.cursor
        try: cursor.executemany(INSERT_CONDITIONS_SQL, self._unsaved)
        except: pass
        finally:
            cursor.close()
            cursor.connection.commit()

        self.__saved = self._unsaved
        self._unsaved = []
    
    def __swap(self) -> 'Control':
        cursor = self.cursor
        try: cursor.executemany(UPDATE_CONDITIONS_SQL, self._unswapped)
        except: pass
        finally: cursor.close(); cursor.connection.commit()

    def select(self, on: str, to: str, at: str):
        cursor = self.cursor
        condition = ''
        try:  condition = cursor.execute(SELECT_CONDITIONS_SQL, {ON: on, TO: to, AT: at}).fetchone()
        except: pass
        finally: cursor.close()

        if condition: return loads(condition[0])

    def __sync(self, database: str, values: list):
        # if db file exists - nuke it
        if path.exists(database): nuke(database)
        self.__db = connect(database)
        self.inits()
        print(values)
        self.__db.cursor().executemany(INSERT_CONDITIONS_SQL, values)
        return True

    @property
    def cursor(self) -> Cursor:
        return self.__db.cursor()

    def add(self, *contracts: 'Contract') -> 'Control':
        def _xtract(k: str, data: dict):
            return k, dumps(data.get(k))
        for contract in contracts:
            if not contract._on: raise ValueError(ON_REQUIRED)
            for action in contract._on:
                payload = contract._payload
                payload['on'] = action
                # self._contracts.append(payload)
                index = f"{action}:{payload['to']}"
                self._contracts[index] = payload
                self._unsaved = [{
                    ON: action,
                    TO: payload['to'],
                    AT: k,
                    DOMAIN: payload[DOMAIN],
                    'condition': condition
                } for k, condition in [_xtract(CONTACT, payload), _xtract(CONTENT, payload), _xtract(CONTEXT, payload)]]
        self.__save()
        return self

    @property
    def condition(self):
        return Condition(self)

    def drop(self, *contracts: 'Contract'):
        vals = []
        for contract in contracts:
            if not contract._on: raise ValueError(ON_REQUIRED)
            for on in contract._on:
                payload = contract._payload
                data = [{DOMAIN: payload[DOMAIN], ON: on, TO: payload['to'], AT: k} for k in [CONTACT, CONTENT, CONTEXT]]
                vals.extend(data)
        self.cursor.executemany(DELETE_CONDITIONS_SQL, vals)

    @property
    def evaluate(self) -> 'Guard':
        """
        If someone tries to evaluate with a can and to and a
        valid contract does not exist then raise an error
        """
        return Guard(self)

    def inits(self) -> 'Control':
        cursor = self.cursor
        try: cursor.executescript(SQL)
        except: pass
        finally: cursor.close()
        return self
    
    def nuke(self, engine: str):
        base = f'{PIDENTITY}/{engine}.db'
        if(Path(base).exists()): Path.unlink(base)
        print(base); print(Path(base).exists())

    def on(self, action: str) -> Conditions:
        c = Conditions(self)
        return c.on(action)

    def to(self, target: str) -> Conditions:
        c = Conditions(self)
        return c.to(target)

    def start(self, action: str):
        return Controller(self)

    def swap(self, *contracts: 'Contract') -> 'Control':
        def _xtract(k: str, data: dict):
            return k, dumps(data.get(k))
        for contract in contracts:
            if not contract._on: raise ValueError(ON_REQUIRED)
            for action in contract._on:
                payload = contract._payload
                payload['on'] = action
                # swap out payload in memory here
                index = f"{action}:{payload['to']}"
                in_memory_payload = self._contracts.get(index)
                if in_memory_payload:
                    for w in [CONTACT, CONTENT, CONTEXT]:
                        in_memory_payload[w] = payload[w]
                self._unswapped = [{
                    ON: action,
                    TO: payload['to'],
                    AT: k,
                    DOMAIN: payload['domain'],
                    'condition': condition
                } for k, condition in [_xtract(CONTACT, payload), _xtract(CONTENT, payload), _xtract(CONTEXT, payload)]]
        self.__swap()
        return self

    def sync(self, engine: str) -> bool:
        """Read engine in .pidentity/{engine}.json and replace .pidentity/{engine}.db with the contents"""
        Path('.pidentity').mkdir(exist_ok=True)
        database = f'{PIDENTITY}/{engine}.db'
        json_string = ''
        try:
            f = open(f'{PIDENTITY}/{engine}.json')
            json_string = f.read()
            f.close()
        except: return False

        json_data = loads(json_string)
        for data in json_data:
            data['condition'] = dumps(data.get('condition', {}))
        return self.__sync(database, json_data)

    @property
    def saved(self):
        saved = self.__saved
        self.__saved = []
        return saved

