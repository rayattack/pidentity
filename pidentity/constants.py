from pidentity.macros import *


CONTACT = "contact"
CONTENT = "content"
CONTEXT = "context"
PIDENTITY = '.pidentity'


ON = 'upon'
TO = 'unto'
AT = 'what'


# think of making this extensible with user provided macros
# by moving this to a config that can be loaded with additional functions
# at coding time or runtime by the developers i.e. something along
# the lines of: contract.macros.add('my_macro', my_macro_func)
# the macro function must accept 2 arguments and return a value
# where this arguments will be passed in the value of the
# contract.context.key value from the contract object that was passed in
# at contract creation time and the control.context.key value
# that will be passed in at contract evaluation time
# i.e. contract.context({'ip': '10.232.14.54'}) has '10.232.14.54' as the creation
# time value and the macro function will be passed this value and
# the one received at evaluation time
# from control.context({'ip': '10.20.20.20'})
# the macro function
# will be responsible for returning if the evaluation passed or failed based on
# the values it received
MACROS = {
    'cidr': placeholder,
    'ip': placeholder,
    'datetime': placeholder,
    'date': placeholder,
    'time': placeholder,
    'memory': placeholder,
    'cpu': placeholder,
    'saturation': placeholder
}


OPERANDS = {
    ":::": "NESTED",
    ":<<": "LT",
    ":<=": "LTE",
    ":>>": "GT",
    ":>=": "GTE",
    ":==": "EQ",
    ":!=": "NEQ",
    ":~~": "REGEX",
    ":??": "IN",
    ":!!": "NIN",
    ":><": "BTW",
    "@<<": "REF",
    "@<=": "REF",
    "@>>": "REF",
    "@>=": "REF",
    "@==": "REF",
    "@!=": "REF",
    "@~~": "REF",
    "@??": "REF",
    "@!!": "REF"
}


OPERATORS = {
    'NESTED': lambda:...,
    'REFIN': lambda:...,
    # etc
}


SYMBOLS = {"?": "OR", "&": "AND"}
