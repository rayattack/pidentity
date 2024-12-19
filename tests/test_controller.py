import os
from pathlib import Path
from unittest import TestCase

from pidentity import Contract, Control, Conditions
from pidentity.operators import IN
from pidentity.constants import CONTACT, CONTENT, CONTEXT, DOMAIN, ON, TO, AT


DB = 'pidentity'


class ConditionsTest(TestCase):
    def setUp(self) -> None:
        self.control = Control(DB)
        self.control.inits()
        self.control.add(Contract().on('yimu').to('pidentity').contact({'username': 'tersoo'}))
        self.control.add(Contract().on('gossip').to('cia').content({'owner': '$contact.username'}))
        self.conditions = Conditions(self.control)
        return super().setUp()

    def tearDown(self):
        self.control.nuke()

    def test_conditions_scan(self):
        control = self.control
        control.add(Contract().on('foo').to('bar').content({'unlocked': True}))
        control.add(Contract().on('baz').to('yan').content({'unlocked': False}))

        cursor = control.cursor
        rows = cursor.execute(f"""
            select * from conditions
                where {ON} = 'baz' and {TO} = 'yan' and what = 'content' and domain = '*'
            """).fetchall()
        cursor.close()
        self.assertEqual(len(rows), 1)

        result = control.select('baz', 'yan', 'content')
        self.assertIsNotNone(result)

        data = control.clean().on('foo').to('bar').at('content').scan()
        print(control._contracts)
        self.assertIsNotNone(data)
        self.assertEqual({'&unlocked:==': True}, data)

    def test_no_go_errors(self):
        can = self.control.on('foo').to('bar').start()
        value = can.content({}).contact({}).context({}).go()
        self.assertFalse(value)

    def test_eval_contact(self):
        can = self.control.on('yimu').to('pidentity').start()
        yes = can.contact({'username': 'tersoo'}).go()
        self.assertTrue(yes)

        controller = self.control.on('yimu').to('pidentity').start()
        no = controller.contact({'username': 'ladi'}).go()
        self.assertFalse(no)

    def test_eval_reference(self):
        can = self.control.on('gossip').to('cia').start()
        yes = can.contact({'username': 'snowden'}).content({'owner': 'snowden'}).go()
        self.assertTrue(yes)

    def test_eval_btw(self):
        ctrl = Control(DB)

    def test_logical_comparisons(self):
        self.control.add(Contract().on('boo').to('haters').content({
            '&user': '$contact.id',
            '?location': IN(['sweden', 'portugal'])
        }))
        can = self.control.on('boo').to('haters').start()
        no = can.content({'user': 40, 'location': 'swede'}).contact({'id': 44}).go()
        yes = can.content({'user': 40, 'location': 'swede'}).contact({'id': 40}).go()
        self.assertTrue(yes)
        self.assertFalse(no)

