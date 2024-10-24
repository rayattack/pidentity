from unittest import TestCase

from pidentity import Contract, Control
from pidentity.constants import CONTACT, CONTENT, CONTEXT


DB = 'pidentity'


class ControlTest(TestCase):
    def setUp(self) -> None:
        self.control = Control(DB)
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
        for i, v in enumerate([CONTACT, CONTENT, CONTEXT]):
            self.assertDictEqual(control._unsaved[i], {
                'activity': 'post',
                'towards': '/customers/:id',
                'regulates': v,
                'conditions': '{}'
            })

    def test_control_raises_when_contract_not_activated(self):
        # every contract must call contract.on.to before being added to controls
        control = Control(engine=DB)
        contract = Contract(domain='mydomain')
        self.assertRaises(ValueError, control.add, contract)

    def test_control_save(self):
        control = Control(engine=DB)
        contract = Contract(domain='mydomain')
        contract.on('post').to('/customers/:id')
        control.add(contract)
        control.save()

    def test_control_drop(self):
        control = Control(engine=DB)
        contract = Contract(domain='mydomain')
        contract.on('post').to('/customers/:id') 
        control.drop(contract)


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
