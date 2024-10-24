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
                'conditions': '{}'
            })
        self.assertListEqual([], control.saved)

        cursor = control.cursor
        one = cursor.execute('select * from regulators').fetchone()
        cursor.close()
        self.assertIsNotNone(one)

    def test_control_drop(self):
        _sql = f"select * from regulators where {TO} = '/orders/:id/line-items'"
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
        rows = cursor.execute("select * from regulators where unto = 'uu7483-eea3a-akdje283-adkea'").fetchall()
        cursor.close()
        self.assertEqual(len(rows), 1)
    
    def test_control_swap(self):
        raise ValueError
