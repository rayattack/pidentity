# CONTROL(ler)
To understand this page you **SHOULD** read the sections - Specifying rules via [Contracts](index.md) with
the `pidentity.Contract` object, combining that with contextual information available to your information
system via [Context](context.md) `pidentity.Context`, and how to
protect valuable data a.k.a [Content](content.md) via the `pidentity.Content` object.


## pidentity.Control

pidentity is all about controlling access to content (data); as such the parent object for all activity is the `pidentity.Control` object, and this
object has only 3 responsibilities

to **`1. save`**, **`2. retrieve`** (scan), and **`evaluate`** contracts. *For more, see* [`pidentity.Contract`](contracts.md).

**Relationship Flow:**

`Control` -> (saves, retrieves, evaluates) -> `Contract(s)`

`Contract(s)` -> (use 3 blocks to say what's legal/illegal) -> [`Content`, `Contact`, `Context`].

- **Content**: Uses information found in the data for access control
- **Context**: Uses information outside data for access control.
- **Contact**: Uses information of the (persona) trying to access the data for access control

**1a: Show me the code?**

```py
from pidentity import Control

control = Control()
```
We'll come back to `pidentity.Control` and its API later once we have finished exploring `pidentity.Contract` and have understood it better - as this will make it easier to understand the `pidentity.Control` object and its [`API`](api/contracts.md).


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
control.add(contract)
await controls.save()

# for synchronous use cases use save sync
controls.saves()
```

```py

# now we can provide some context, content, and contact rules/conditions we
# want to combine with the possible actions specified above

c.context({})  # empty dict (allows everything) but good enough for now
c.content({})  # empty dict for now
c.contact({})  # empty dict for now


# finally let's add this contract to our controls for saving so it can be used later
# await protocol.add_contract(c) also possible
control.add(c)
```

#### Contact
This is recorded personal identifying information that can be used to identify a persona (app, human etc). Contact blocks are how you tell pidentity to
target personas. As usual - let's look at some code.

```py
```
