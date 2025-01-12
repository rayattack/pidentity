import os
from pathlib import Path
from unittest import TestCase

from pidentity import Contract, Controls, Conditions
from pidentity.constants import CONTACT, CONTENT, CONTEXT, DOMAIN, ON, TO, AT


DB = 'pidentity'


class ConditionsTest(TestCase):
    def setUp(self) -> None:
        self.control = Controls('conditions')
        self.control.inits()
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
