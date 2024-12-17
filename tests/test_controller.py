import os
from pathlib import Path
from unittest import TestCase

from pidentity import Contract, Control, Conditions
from pidentity.constants import CONTACT, CONTENT, CONTEXT, DOMAIN, ON, TO, AT


DB = 'pidentity'


class ConditionsTest(TestCase):
    def setUp(self) -> None:
        self.control = Control('conditions')
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

        rows = control.cursor.execute(f"select * from conditions where {TO} = 'yan' and what = 'content'").fetchall()
        self.assertEqual(len(rows), 1)

        result = control.select('baz', 'yan', 'content')
        self.assertIsNotNone(result)

        data = control.clean().on('foo').to('bar').at('content').scan()
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

