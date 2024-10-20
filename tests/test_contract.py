from unittest import TestCase
from datetime import datetime

from pydentity.contract import Contract
from pydentity.operators import IN


class ContractTest(TestCase):
    def test_contract_payload_structure(self):
        contract = Contract(domain='mydomain')
        payload = contract._payload
        self.assertIsInstance(payload, dict)
        self.assertEqual(payload['domain'], 'mydomain')
        self.assertEqual(payload['to'], '')
        self.assertEqual(payload['on'], '')
        self.assertEqual(payload['contact'], {})
        self.assertEqual(payload['content'], {})
        self.assertEqual(payload['context'], {})
        self.assertEqual(contract._on, [])

    def test_contract_on(self):
        contract = Contract(domain='mydomain')
        contract.on('post')
        self.assertEqual(contract._on[0], 'post')

        # replace existing
        contract.on('put', 'get')
        self.assertEqual(contract._on[0], 'put')
        self.assertEqual(contract._on[1], 'get')
    
    def test_contract_to(self):
        contract = Contract(domain='mydomain')
        contract.to('/customers/:id')
        self.assertEqual(contract._payload['to'], '/customers/:id')
    
    def test_contract_contact(self):
        contract = Contract(domain='mydomain')
        self.assertEqual(contract._payload['contact'], {})
        contact = {'id': 10}
        contract.contact(contact)
        self.assertEqual(contract._payload['contact'].get('&id:=='), 10)
    
    def test_contract_content(self):
        contract = Contract(domain='mydomain')
        self.assertEqual(contract._payload['content'], {})
        content = {'id': 10}
        contract.content(content)
        self.assertEqual(contract._payload['content'].get('&id:=='), 10)
    
    def test_contract_context(self):
        now = datetime.now()
        contract = Contract(domain='mydomain')
        self.assertEqual(contract._payload['context'], {})
        context = {'datetime': now}
        contract.context(context)
        self.assertEqual(contract._payload['context'].get('&datetime:=='), now)

    def test_contract_context_accepts_only_macros(self):
        contract = Contract(domain='mydomain')
        context = {'dt': datetime.now()}
        with self.assertRaises(ValueError):
            contract.context(context)

    def test_contract_this(self):
        contract = Contract(domain='mydomain')
        contact = {
            'id': '132313122',
            'location': contract.this('context.location')
        }
        _expected = { '&id:==': '132313122', '&location@==': 'context.location' }
        contract.contact(contact)
        self.assertDictEqual(contract._payload['contact'], _expected)

    def test_contract_prepare(self):
        contract = Contract(domain='mydomain')
        data = {
            'id': '132313122',
            'name': 'John Doe',
            'age': 18,
            'location': contract.this('context.location'),
            'reference': IN(contract.this('contact.id')),
            'address': {
                'city': 'New York',
                'state': 'NY',
            }
        }
        _expected = {
            '&id:==': '132313122',
            '&name:==': 'John Doe',
            '&age:==': 18,
            '&location@==': 'context.location',
            '&reference@??': 'contact.id',
            '&address:::': {
                '&city:==': 'New York',
                '&state:==': 'NY',
            }
        }
        self.assertDictEqual(contract.prepare(data), _expected)
