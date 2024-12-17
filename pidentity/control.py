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
from pidentity.macros import Operation, OPERATIONS


ON_REQUIRED = 'Every contract must have a valid action and destination before being added to a control'



class Controller(object):
    def __init__(self, conditions):
        self.__ctrl = conditions.control
        self.__conditions = conditions
        self.__stores = {}  # determine on which to keep and which to throw away

    def __extract(self, pathway):
        print('We saw ourself here in the field: ', pathway)
        print('*' * 50)
        pathways = pathway.split('.')
        data = self.__stores
        for part in pathways:
            data = data.get(part)
        return data

    def __parse_rule_key(self, key):
        logic = key[0]
        field = key[1:-3]
        op = OPERATIONS.get(key[-3:])
        return logic, field, op

    def __parse_rule_value(self, field):
        prefix = field.split('.')[0]
        if prefix in ['$content', '$context', '$contact']:
            return field, None
        return None, field

    def content(self, values: dict):
        self.__stores['$content'] = values
        return self

    def context(self, values: dict):
        self.__stores['$context'] = values
        return self

    def contact(self, values: dict):
        self.__stores['$contact'] = values
        return self

    def evaluator(self, rules, data):
        """
        Evaluate the condition i.e. {
            '&id:==': '132313122',
            '&name:==': 'John Doe',
            '&age:==': 18,
            '&location@==': '$context.location',
            '&reference@??': '$contact.id',
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
        for key, value in rules.items():
            # logic = & || or, field = key i.e. id, operator = Operator() instance
            logic, field, operation = self.__parse_rule_key(key)

            # reference == $lookup path or None, datum is the actual data or the $store i.e. context, content etc if reference is True
            # if actual value we keep it to be used in comparison operation
            # if it is a reference then get the actual value to be used in comparison operation
            reference, value_in_rules = self.__parse_rule_value(value)
            if reference: value_in_rules = self.__extract(reference)
                    
            # check if the field passes validation for the commensurate rules
            value_in_data = data.get(field)
            if (not value_in_data) and (logic == '&'): return False
            if (not operation(value_in_rules, value_in_data)) and (logic == '&'): return False
        return True
    
    def go(self) -> bool:
        conditions, good = [], []
        that = self.__conditions
        for o in ['$content', '$context', '$contact']:
            data = self.__stores.get(o)
            if(data):
                # get the rules / conditions from memory or storage and log it
                rules = {'$content': that.content, '$context': that.context, '$contact': that.contact}.get(o)
                if not rules: continue
                conditions.append((rules, data))

        if not conditions: return False
        for condition in conditions:
            rules, data = condition
            good.append(self.evaluator(rules = rules, data = data))

        return all(good)


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


class Control(object):
    def __init__(self, engine: str):
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

