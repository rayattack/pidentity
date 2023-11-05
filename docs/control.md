
To understand this page you **SHOULD** read the [Getting Started Section](index.md) and install `Pydentity` using the instructions provided at the bottom of the page.

## The Control Object

Pydentity is all about controlling access to content (data); as such the parent object for all activity is the `pydentity.Control` object, and this
object has only 3 responsibilities

to **`1. save`**, **`2. retrieve`**, and **`evaluate`** contracts. *For more, see* [`pydentity.Contract`](contracts.md).

**Relationship Flow:**

`Control` -> (saves, retrieves, evaluates) -> `Contract(s)`

`Contract(s)` -> (use 3 blocks to say what's legal/illegal) -> [`Content`, `Contact`, `Context`].

- **Content**: Uses information found in the data for access control
- **Context**: Uses information outside data for access control.
- **Contact**: Uses information of the (persona) trying to access the data for access control

Show me the code?

```py
from pydentity import Control

control = Control()
```
We'll come back to `pydentity.Control` and its API later once we have finished exploring `pydentity.Contract` and have understood it better - as this will make it easier to understand the `pydentity.Control` object and its [`API`](api/contracts.md).
