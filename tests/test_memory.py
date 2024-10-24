from pidentity import Contract, Control


contract = Contract(domain='mydomain')
control = Control(engine='myengine')

contract.on('post').to('/customers/:id')