from json import dumps, loads
from os import environ, path, remove as nuke
from pathlib import Path
from sqlite3 import Cursor, connect, Connection

from pidentity import Conditions, Contract
from pidentity.constants import CONTACT, CONTENT, CONTEXT, DOMAIN, PIDENTITY, ON, TO, AT
from pidentity.database import (
    DELETE_CONDITIONS_SQL,
    INSERT_CONDITIONS_SQL,
    UPDATE_CONDITIONS_SQL,
    SELECT_CONDITIONS_SQL,
    SQL
)


ON_REQUIRED = 'Every contract must have a valid action and destination before being added to a control'


class Control(object):
    def __init__(self, engine: str = 'hashmap'):
        self._contracts = {}  # ['post:@:/v1/customers/:id', 'get:@:/v1/customers/id']
        self.__engine = engine
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

    def select(self, on: str, to: str, at: str, domain = '*'):
        cursor = self.cursor
        condition = ''
        try:  condition = cursor.execute(SELECT_CONDITIONS_SQL, {ON: on, TO: to, AT: at, DOMAIN: domain}).fetchone()
        except: pass
        finally: cursor.close()
        if condition: return loads(condition[0])

    def load(self, folder: str, ext = '.json'):
        return self

    def __sync(self, database: str, values: list):
        # TODO: this should be unsync not sync
        # if db file exists - nuke it
        if path.exists(database): nuke(database)
        self.__db = connect(database)
        self.inits()
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

    def clean(self):
        self._contracts = {}  # ['post:@:/v1/customers/:id', 'get:@:/v1/customers/id']
        self.__db = connect(f'.pidentity/{self.__engine}.db')
        self._unsaved = []
        self._unswapped = []
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
    
    def nuke(self, engine: str = None):
        _engine = engine or self.__engine
        base = f'{PIDENTITY}/{_engine}.db'
        if(Path(base).exists()): Path.unlink(base)

    def on(self, action: str) -> Conditions:
        c = Conditions(self)
        return c.on(action)

    def to(self, target: str) -> Conditions:
        c = Conditions(self)
        return c.to(target)

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

    def sync(self, engine: str = None) -> bool:
        """Read engine in .pidentity/{engine}.json and replace .pidentity/{engine}.db with the contents"""
        _engine = engine or self.__engine
        Path('.pidentity').mkdir(exist_ok=True)
        database = f'{PIDENTITY}/{_engine}.db'
        json_string = ''
        try:
            f = open(f'{PIDENTITY}/{_engine}.json')
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

