import os
from pathlib import Path
from unittest import TestCase

from pidentity import Contract, Control
from pidentity.constants import CONTACT, CONTENT, CONTEXT, ON, TO, AT


DB = 'pidentity'


class ControlTest(TestCase):
    def setUp(self) -> None:
        self.control = Control(DB)
        self.control.inits()
        return super().setUp()

    def test_control_payload_structure(self):
        control = Control(engine=DB)
        self.assertEqual(control._contracts, [])

    def test_control_init(self):
        self.control.inits()

    def test_control_add(self):
        control = Control(engine=DB)
        contract = Contract(domain='mydomain')
        contract.on('post').to('/customers/:id')
        control.add(contract)
        self.assertEqual(control._contracts[0], contract._payload)

        saved = control.saved
        for i, v in enumerate([CONTACT, CONTENT, CONTEXT]):
            self.assertDictEqual(saved[i], {
                ON: 'post',
                TO: '/customers/:id',
                AT: v,
                'condition': '{}'
            })
        self.assertListEqual([], control.saved)

        cursor = control.cursor
        one = cursor.execute('select * from conditions').fetchone()
        cursor.close()
        self.assertIsNotNone(one)

    def test_control_drop(self):
        _sql = f"select * from conditions where {TO} = '/orders/:id/line-items'"
        control = Control(engine=DB)
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
        control = Control(engine=DB)
        contract = Contract(domain='mydomain')
        self.assertRaises(ValueError, control.add, contract)

    def test_control_content_evaluation(self):
        control = Control(engine=DB)
        contract = Contract(domain='mydomain')
        contract.on('post').to('/customers/:id')
        contract.content({'owner': contract.this('contact.owner')})
        control.add(contract)

        # return a fresh control that does not pollute the original
        guard = control.guard()
        guard = guard.on('post').to('/customers/:id')
        guard.content({
            'owner': 10,
            'name': 'iPhone 15 pro'
        }).context({
            'ip': '10.13.13.13'
        }).contact({
            'owner': 10
        })
        self.assertTrue(guard.scans())

    def test_control_sync(self):
        self.assertTrue(self.control.sync('test'))
        self.assertTrue(Path('.pidentity/test.json').exists())
        self.assertTrue(Path('.pidentity/test.db').exists())

        cursor = self.control.cursor
        rows = cursor.execute("select * from conditions where unto = 'uu7483-eea3a-akdje283-adkea'").fetchall()
        cursor.close()
        self.assertEqual(len(rows), 1)
        self.control.nuke('test')

    def test_control_nuke(self):
        control = Control('bandana')
        control.inits()
        self.assertTrue(Path('.pidentity/bandana.db').exists())

        control.nuke('bandana')
        self.assertFalse(Path('.pidentity/bandana.db').exists())

    def test_control_swap(self):
        ctrl = Control('swapper').inits()
        ctrl.add(Contract().on('foo').to('10001').contact({"identifier": 10001}))
        ctrl.add(Contract().on('bar').to('10001').content({"unlocked": True}))
        contract = ctrl._contracts[0]

        contact = ctrl.condition.on('foo').to('10001').contact
        self.assertIsNotNone(contact)
        self.assertEqual(contract.get('contact'), contact)

        ctrl.swap(Contract().on('foo').to('10001').contact({"identifier": 10002}))
        contact = ctrl.condition.on('foo').to('10001').contact
        self.assertEqual(contact.get('&identifier:=='), 10002)
