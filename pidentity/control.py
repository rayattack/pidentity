from json import dumps, loads
from os import environ, path, remove as nuke
from pathlib import Path
from sqlite3 import Cursor, connect, Connection

from pidentity import Conditions, Contract
from pidentity.constants import CONTACT, CONTENT, CONTEXT, DOMAIN, PIDENTITY, ON, TO, AT
from pidentity.database import (
    DELETE_CONDITIONS_SQL,
    INSERT_CONDITIONS_SQL,
    UPSERT_CONDITIONS_SQL,
    UPDATE_CONDITIONS_SQL,
    SELECT_CONDITIONS_SQL,
    SQL
)


ON_REQUIRED = 'Every contract must have a valid action and destination before being added to a control'


def CONNECT_SQLITE(dbfile: str, timeout = 3):
    return connect(dbfile, isolation_level = None)


class Control(object):
    def __init__(self, engine: str = 'hashmap'):
        self.__db = None
        self._contracts = {}  # ['post:@:/v1/customers/:id', 'get:@:/v1/customers/id']
        self.__engine = engine
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
        try: cursor.executemany(UPSERT_CONDITIONS_SQL, self._unsaved)
        except IndexError: pass
        finally:
            cursor.close()
            cursor.connection.commit()

        self.__saved = self._unsaved
        self._unsaved = []
        return self
    
    def __swap(self) -> 'Control':
        cursor = self.cursor
        try: cursor.executemany(UPDATE_CONDITIONS_SQL, self._unswapped)
        except: pass
        finally: cursor.close(); cursor.connection.commit()
        return self

    def select(self, on: str, to: str, at: str, domain = '*'):
        cursor = self.cursor
        condition = ''
        try:  condition = cursor.execute(SELECT_CONDITIONS_SQL, {ON: on, TO: to, AT: at, DOMAIN: domain}).fetchone()
        except: pass
        finally: cursor.close()
        if condition: return loads(condition[0])

    def load(self, folder: str, ext = '.json'):
        return self

    def __sync(self, values: list):
        # TODO: this should be unsync not sync
        # if db file exists - nuke it
        if not self.__db: raise ValueError('Database not yet initialised')
        cursor = self.__db.cursor()
        cursor.executemany(INSERT_CONDITIONS_SQL, values)

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
                    'condition': condition,
                    'metadata': dumps(contract.metadata())
                } for k, condition in [_xtract(CONTACT, payload), _xtract(CONTENT, payload), _xtract(CONTEXT, payload)]]
        self.__save()
        return self

    def clean(self):
        self._contracts = {}  # ['post:@:/v1/customers/:id', 'get:@:/v1/customers/id']
        self.__db = CONNECT_SQLITE(f'.pidentity/{self.__engine}.db', timeout = 3)
        self._unsaved = []
        self._unswapped = []
        return self

    @property
    def conditions(self):
        return Conditions(self)

    def drop(self, *contracts: 'Contract'):
        vals = []
        for contract in contracts:
            if not contract._on: raise ValueError(ON_REQUIRED)
            for on in contract._on:
                payload = contract._payload
                data = [{DOMAIN: payload[DOMAIN], ON: on, TO: payload['to'], AT: k} for k in [CONTACT, CONTENT, CONTEXT]]
                vals.extend(data)
        self.cursor.executemany(DELETE_CONDITIONS_SQL, vals)

    def inits(self, config = None) -> 'Control':
        """Read engine in .pidentity/{engine}.json and replace .pidentity/{engine}.db with the contents"""
        Path('.pidentity').mkdir(exist_ok=True)
        way = f'.pidentity/{self.__engine}.db'
        if Path(way).exists():
            self.__db = CONNECT_SQLITE(way)
            return self
        self.__db = CONNECT_SQLITE(way, timeout = 3)
        cursor = self.__db.cursor()
        try: cursor.executescript(SQL)
        except: pass
        finally: cursor.close()
        if config:
            self.sync(config)
        return self
    
    def nuke(self, engine: str = ''):
        _engine = engine or self.__engine
        base = f'{PIDENTITY}/{_engine}.db'
        _base = Path(base)
        if(_base.exists()): _base.unlink(missing_ok = True)

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

    def sync(self, config: str = None) -> bool:
        json_string = ''
        with open(f'{PIDENTITY}/{config}.json') as f:
            json_string = f.read()
        json_data = loads(json_string)
        for data in json_data:
            data['condition'] = dumps(data.get('condition', {}))
            data['metadata'] = dumps(data.get('metadata', {}))
        self.__sync(json_data)
        return True

    @property
    def saved(self):
        saved = self.__saved
        self.__saved = []
        return saved
