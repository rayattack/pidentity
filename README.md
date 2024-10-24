# Contracts, Policies
Pidentity is an authorization and access control library built to provide simple yet robust ABAC
paradigms. (**NOTE: Pidentity is not a strict ABAC system**) - it is simpler but without
sacrificing the power of ABAC.


## Components
pidentity works on a &copy; Micro `C5 Paradigm` which translates
to **`Control Content from Contact via Contracts Contextually`**. Sounds
intimidating but it is really simple once broken down.


Every information system has:

- **Content**: this is the data you might want to protect i.e. data stored in the system or system(s)

- **Contacts**: Entities that want to come in contact with the data (owner of the data, someone
granted access by owner, hacker, application) etc.

- **Context**: Information within the information system or that the information system has access
to but exists outside of the **Content** or protected data i.e. dates or times when no one is allowed
to update content, ip address of a contact etc.

- **Contracts**: What is a legal or illegal operation when **Content**, **Contact**, **Context** is combined together

- **Controls**: The system, processes, tools etc. that deny or allows operations _to_ and _on_ content

So how does this all relate to C5 - From the definition it means:
You (your application, company) wants to **control** (allow, deny access _to_ or limit actions _on_) **content** (data, information)
from **contact** (application, hacker, human) via **contracts** (combinatory rules) **contextually** (which might include the
use of data not stored within the content being controlled).


## Contracts
The first thing to understand is _Contracts_. Contracts are how you specify the relationships
betweem **_Contacts_** and **_Content_**. How do we create Contracts? Let's look at some code

##### Code Snippet: 1a
```py
from pidentity import Contract

contract = Contract()
```


Simple enough, but then, how do you tell a contract what actions are possible, and how to identify **Content** to be **Control**led?

##### Code Snippet: 1b
```py
...  # code from above

contract.on('delete').to('/customers/:id')
```
To specify actions use the `.on(*actions)` method of the contracts object. Actions can be called whatever you
want i.e. `.on('foo')` - for web applications `HTTP` verbs can be an intuitive option or popular candidate.

It is also important to note that all **contract** object method calls are order agnostic, this means you called have
also called the `.to('/customers/:id')` method before the `.on('deletes')` method and still get the same output.

This means the code snippet in snippet `1b` above is equivalent to code in snippet `1c` below.

##### Code Snippet: 1c
```py
contract.to('/customers/:id').on('delete') 
```


### Contract Rules &amp; Conditions
Great, now we know how to build a contract and tell it what actions and **Content** `.to('a-unique-id-for-content')` it
identifies. But a contract is useless if we have no way of specifying the
actual `content`, `contact`, and `context` data for which the contract is valid.


#### Controlling Access Based On Content
If you want to control access to content based on the data in the content itself - you tell your contract this by
using the `.content(conditions: dict)` method of the `contract` object. It is important to note that by
default **`pidentity denies all access unless a contract is found`**.


```py
from pidentity import Contract


# pidentity by default denies all access where there is no contract
# so to delete unlocked orders - this contract is needed
c = Contract()
c.on('delete').to('orders').content({
    'unlocked': True
})


# this will allow any content at the address `/orders/:id` with category
# `Perishables` to be deleted
d = Contract()
d.on('delete').to('/orders/:id').contact({
    'category': 'Perishables'
})
```
We are going to cover `Contact`, and `Context` blocks in later sections, but before we do it is important to explain how their configurations dictionary works. Dictionaries, hashmaps,
associative arrays (different names for the same thing) have a common format - `a key` maps to `a value`.
pidentity *conditions* i.e. `.contact(**conditions)`, `.content(**conditions)`, `.context(**conditions)` are dictionaries that are passed into the *content*, *contact*, and *context* `pidentity.Contract`
methods.

By default `condition keys` i.e. dict keys are used for specifying what fields in the block(s) - (content, contact, context) to target, and the `values` provide indication of what the value of those fields
should be i.e. `constant values` expected to be seen for given contract conditions.

For all condition dicts across all blocks i.e. `content, context, contact` - the default
combination logic is `AND` i.e.

```json
{"key": 0, "key2": 1}
```

means where key = 0 `AND` key2 = 1

and **`is the same as`**

```json
{"&key": 0, "&key2": 1}
```

this is because `&` as the default symbol for `condition keys`, in addition, `AND` is the default operation for condition dictionaries when no symbol is explicitly provided.

To use `OR` logic instead of `AND`, use the **OR** symbol `?` as the first character of your conditions dict i.e.

```py
from pidentity import Contract
from pidentity.conditions import GT  # other options -> GTE, LT, BETWEEN, IN, NIN etc


# this contract will allow
#   any contact
# to retrieve
#   any content
# where
#   name = 'Jon' OR age > 18
Contract().on('gets').to('/customers').content({
    '?name': 'Jon',
    '?age': GT(18)
})


# OR, AND and others are non greedy and top to bottom
# that means &age, &name, ?role, &department
```

```py
c = Contract()

# this contract means give everyone access when orders content is public AND unlocked
c.on('gets').to('/orders').content({
    'public': True,
    'unlocked': True
})

# this is the same as above but using explicit symbol notation
c.on('gets').to('/orders').content({
    '&public': True,
    '&unlocked': True
})


# this contract means give everyone access when orders content is public OR unlocked
c.on('gets').to('/orders').content({
    '?public': True,
    '?unlocked': True
})
```
To specify `OR` combinations the keys must use the explicit symbol notation with the symbol for `OR` which is a `?`.

```py
c = Contract()

# this contract means allow Contact to the content
# at address `/products/:id` when it is public OR unlocked
c.on('updates').to('/products/:id').content({
    '?public': True,
    '?unlocked': True
})
```

```py
from pidentity import Controls

... # code from previous block here

controls = Controls()
controls.add(c, d)
```
These contracts are loaded in memory and for test use cases that is fine, but to make the most of pidentity you might want to connect a storage engine
like a database for contracts to be saved and retrieved easily.

Currently only redis, postgres, sql server, oracle db, and mysql is supported as a storage engine.

```py
from pidentity import Contract, Controls

controls = Controls(engine='postgres', dsn=...)
contract = Contract()

contract.on('patches').to('/customers/:id').context({
    'cidr': '10.0.0.0/24'
})
# contracts above are added in-memory but not saved, to persist contracts?
await controls.save()

# for synchronous use cases use save sync
controls.saves()
```

```

# now we can provide some context, content, and contact rules/conditions we
# want to combine with the possible actions specified above

c.context({})  # let's use an empty dict for now - this will allow everyone but it's good enough for now
c.content({})  # empty dict for now
c.contact({})  # empty dict for now


# finally let's add this contract to our controls for saving so it can be used later
# await protocol.add_contract(c) also possible
protocol.add_contract_sync(c)
```


```py
# this will allow any contact with first_name of Tersoo to delete an order
d = Contract()
d.on('delete').to('orders/:id').contact({
    'first_name': 'Tersoo'
})
```


#### Contact
This is recorded personal identifying information that can be used to identify a persona (app, human etc).



## Crash Course
pidentity is all about **identifying** _contacts_, protecting _content_, they can have access _to_, as well as the _context_ for that access to be valid. There are a few things to note about pidentity namely:

- Context: 