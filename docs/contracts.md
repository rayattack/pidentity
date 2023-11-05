# Contracts
The first thing to therefore understand is _Contracts_. Contracts combine _Content_, _Contact_, and _Content_ blocks to capture what data action (retrieval, update etc) should
be **allowed** (legal) or **rejected** (illegal).

### What's In A Contract


How do we create Contracts? Let's look at some code

```py
from pydentity import Contract

contract = Contract()
```

Stupid simple no? But then, how do you tell a contract what actions are possible, and how to identify content to be controlled? Let's look at some more code to figure
it out.

```py
...  # code from above

contract.on('deletes').to('/customer/:id')
```

!!! note
    It is important to note that all contract method calls are order agnostic, this means you called have also called the `.to('/customers/:id')` method before
    the `.on('deletes')` method and still get the same output.

As shown above, you need to use the `.on(*actions)` method of the `contract: Contract` object to tell a *contract* what action(s) it should focus on. Actions can be called whatever you want i.e. `.on('foo')` but pluralized `HTTP` verbs are a popular choice.


```py
...  # contract.to('/customers/:id').on('deletes', 'posts')
```

The example above also show the use of the `.to(location: str)` method that accepts a friendly name that is used together with the *action* to identify, save, and later retrieve this contract.

!!! note

    The **action**, and **location** form the unique identity of a contract i.e. if you have **`100`** **.on(deletes).to('/customer/:id')** contracts **ALL of them** will be evaluated
    whenever the `control: pydentity.Control` object is asked to evaluate a **deletes** action **to** the `/customers/:id` **location**.


### Rules &amp; Conditions
Great, now we know how to build a contract and tell it what actions and content it identifies. But a contract is useless if we have no way of specifying the
`content`, `contract`, and `context` conditions for which the contract is valid.


### Content Based Control
If you want to control access to content based on the data in the content itself - you tell your contract this by using the `.content(conditions: dict)` method
of the `contract` object. It is important to note that by default **`pydentity denies all access unless a contract is found`**.

```py
from pydentity import Contract


# pydentity by default denies all access where there is no contract
# so to delete unlocked orders - this contract is needed
c = Contract()
c.on('deletes').to('orders').content({
    'unlocked': True
})


# this will allow any contact with first_name of Tersoo to delete an order
d = Contract()
d.on('deletes').to('orders/:id').contact({
    'first_name': 'Tersoo'
})
```
We are going to cover `Contact`, and `Context` blocks in later sections, but before we do it is important to explain how their configurations dictionary works. Dictionaries, hashmaps,
associative arrays (different names for the same thing) have a common format - `a key` maps to `a value`. By default `condition keys` i.e. dict keys are used for specifying what fields
in the block to target, and the `values` provide indication of what the value of those fields should be i.e. `constant values` expected to be seen for given contract conditions.

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
from pydentity import Contract
from pydentity.conditions import GT  # other options -> GTE, LT, BETWEEN, IN, NIN etc


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
```

```py
c = Contract()

# this contract means orders content is public AND unlocked
c.on('gets').to('/orders').content({
    'public': True,
    'unlocked': True
})

# explicit symbol notation
c.on('gets').to('/orders').content({
    '&public': True,
    '&unlocked': True
})
```
To specify `OR` combinations the keys must use the explicit symbol notation with the symbol for `OR` which is a `?`.

```py
c = Contract()

# this contract means products is public OR unlocked
c.on('updates').to('/products/:id').content({
    '?public': True,
    '?unlocked': True
})
```

```py
from pydentity import Controls

... # code from previous block here

controls = Controls()
controls.add(c, d)
```
These contracts are loaded in memory and for test use cases that is fine, but to make the most of pydentity you might want to connect a storage engine
like a database for contracts to be saved and retrieved easily.

Currently only redis, postgres, sql server, oracle db, and mysql is supported as a storage engine.

```py
from pydentity import Contract, Controls

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

```py

# now we can provide some context, content, and contact rules/conditions we
# want to combine with the possible actions specified above

c.context({})  # let's use an empty dict for now - this will allow everyone but it's good enough for now
c.content({})  # empty dict for now
c.contact({})  # empty dict for now


# finally let's add this contract to our controls for saving so it can be used later
# await protocol.add_contract(c) also possible
protocol.add_contract_sync(c)
```

#### Contact
This is recorded personal identifying information that can be used to identify a persona (app, human etc). Contact blocks are how you tell pydentity to
target personas. As usual - let's look at some code.

```py
```
