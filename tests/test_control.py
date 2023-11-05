from unittest import TestCase

from pydentity import Contract, Control


class ControlTest(TestCase):
    def test_control_payload_structure(self):
        control = Control(engine='myengine')
        self.assertEqual(control._contracts, [])

    def test_control_add(self):
        control = Control(engine='myengine')
        contract = Contract(domain='mydomain')
        contract.on('post').to('/customers/:id')
        control.add(contract)
        self.assertEqual(control._contracts[0], contract._payload)

    def test_control_raises_when_contract_not_activated(self):
        # every contract must call contract.on.to before being added to controls
        control = Control(engine='myengine')
        contract = Contract(domain='mydomain')
        self.assertRaises(ValueError, control.add, contract)

    def test_control_save(self):
        control = Control(engine='myengine')
        contract = Contract(domain='mydomain')
        contract.on('post').to('/customers/:id')
        control.add(contract)
        control.save()

    def test_control_content_evaluation(self):
        control = Control(engine='myengine')
        contract = Contract(domain='mydomain')
        contract.on('post').to('/customers/:id')
        contract.content({'id': 10})
        control.add(contract)

        # return a fresh control that does not pollute the original
        guard = control.start
        guard.on('post').to('/customers/:id')
        guard.content({'id': 10, 'name': 'iPhone 15 pro'})
        guard.context({'ip': '10.13.13.13'})
        guard.contact({'email': 'ortserga@gmail.com'})
        self.assertTrue(guard.accepts)
        self.assertFalse(guard.rejects)
