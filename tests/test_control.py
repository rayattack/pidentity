import os
from pathlib import Path
from unittest import TestCase

from pidentity import Contract, Controls, Controller
from pidentity.conditions import Conditions
from pidentity.constants import CONTACT, CONTENT, CONTEXT, DOMAIN, ON, TO, AT


DB = 'pidentity'


class ControlsTest(TestCase):
    def setUp(self) -> None:
        self.control = Controls(DB)
        self.control.inits()
        return super().setUp()

    def test_control_payload_structure(self):
        control = Controls(engine=DB)
        self.assertEqual(control._contracts, {})

    def test_control_init(self):
        self.assertTrue(Path(f'.pidentity/{DB}.db').exists())

    def test_control_add(self):
        control = self.control
        contract = Contract(domain='mydomain')
        contract.on('post').to('/customers/:id')
        control.add(contract)

        x = control._contracts.get('post:/customers/:id')
        self.assertEqual(x, contract._payload)

        saved = control.saved
        for i, v in enumerate([CONTACT, CONTENT, CONTEXT]):
            self.assertDictEqual(saved[i], {
                ON: 'post',
                TO: '/customers/:id',
                AT: v,
                DOMAIN: 'mydomain',
                'condition': '{}',
                'metadata': '{}'
            })
        self.assertListEqual([], control.saved)

        cursor = control.cursor
        one = cursor.execute('select * from conditions').fetchone()
        cursor.close()
        self.assertIsNotNone(one)

    def test_control_drop(self):
        _sql = f"select * from conditions where {TO} = '/orders/:id/line-items'"
        control = self.control
        contract = Contract()
        control.add(
        contract.upon('post', 'get', 'put', 'delete', 'patch').unto('/orders/:id/line-items'))
        cursor = control.cursor.execute(_sql)
        rows = cursor.fetchall()
        cursor.close()
        self.assertEqual(len(rows), 3)

        control.drop(contract)
        cursor = control.cursor.execute(_sql)
        rows = cursor.fetchall()
        cursor.close()
        self.assertEqual(len(rows), 0)


    def test_control_raises_when_contract_not_activated(self):
        # every contract must call contract.on.to before being added to controls
        control = Controls(engine=DB)
        contract = Contract(domain='mydomain')
        self.assertRaises(ValueError, control.add, contract)

    def test_control_clean(self):
        self.control.add(Contract().on('foo').to('bar').content({'yes': True}))
        self.assertNotEqual({}, self.control._contracts)
        self.control.clean()
        self.assertEqual(self.control._contracts, {})

    def test_control_content_evaluation(self):
        control = self.control
        contract = Contract(domain='mydomain')
        contract.on('post').to('/customers/:id')
        contract.content({'owner': contract.this('contact.owner')})
        control.add(contract)

        # return a fresh control that does not pollute the original
        condition = control.on('post').to('/customers/:id')
        self.assertIsInstance(condition, Conditions)

    def test_control_sync(self):
        self.assertTrue(self.control.sync('test'))
        self.assertTrue(Path('.pidentity/test.json').exists())

        cursor = self.control.cursor
        rows = cursor.execute("select * from conditions where unto = 'uu7483-eea3a-akdje283-adkea'").fetchall()
        cursor.close()
        self.assertEqual(len(rows), 1)
        self.control.nuke('test')

    def test_control_nuke(self):
        control = Controls('bandana')
        control.inits()
        self.assertTrue(Path('.pidentity/bandana.db').exists())

        control.nuke('bandana')
        self.assertFalse(Path('.pidentity/bandana.db').exists())

    def test_control_swap(self):
        ctrl = self.control
        ctrl.add(Contract().on('foo').to('10001').contact({"identifier": 10001}))
        ctrl.add(Contract().on('bar').to('10001').content({"unlocked": True}))
        contract = ctrl._contracts.get('foo:10001')

        contact = ctrl.on('foo').to('10001').contact
        self.assertIsNotNone(contact)
        self.assertEqual(contract.get('contact'), contact)

        ctrl.swap(Contract().on('foo').to('10001').contact({"identifier": 10002}))
        contact = ctrl.on('foo').to('10001').contact
        self.assertEqual(contact.get('&identifier:=='), 10002)
