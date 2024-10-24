# The Control Object

To understand this page you **SHOULD** read the [Getting Started Section](index.md) and install `pidentity` using the instructions provided at the bottom of the page.

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
