from pidentity import Contract, Control
# from pidentity.rules import BTW, EQUALS, LT, GT, LTE, GTE, NEQ, IN, NIN, REGEX



# you can limit a policy to a specific domain (optional)
control = Control(dsn='redis://localhost:6379/0')
contract = Contract(domain='mydomain')


# to -> target
# on -> actions
# context matching is for data not in the target content
# if no context is provided during validation stage and keys here are not recognized macros (ip, date, time, etc) then your policy will not match
policy = contract.on('post').to(
    '/customers/:id'
).context({
    '?date': BTW('2020-01-01', '2020-01-02'),
    '?ip': BTW('192.128.0.10/22')  #CIDR notation or IP range if one is provided it is assumed to be cidr
}).content({
    '&name': EQUALS('John Doe'),
    '?age>>': GT(18),
    '&email': REGEX('someone@gmail.*'),
    '&phone': IN(['+1-555-555-5555', '+1-555-555-5556']),
    '&address.city': EQUALS('New York'),
    '?address.state': EQUALS('NY'),
    '&address.zip': EQUALS('10001'),
    '&location': EQUALS(contract.this('contact.location')),
    '&ip': EQUALS(contract.this('context.ip')),
}).contact({
    '&id': '132313122',
    '?name': 'John Doe',
})


if control.run().content({}).contact({}).context({}).can('post'):
    print('yes')
