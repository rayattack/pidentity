# Pidentity : Authorization Simplified
pidentity is an authorization and access control library built to provide simple yet robust ABAC paradigms. (**NOTE: pidentity does not use ABAC XACML or ABAC conventions**) - it
uses an insanely simpler paradigm to solve the same problem.


## The pidentity Paradigm
pidentity works via its own custom `C5 Paradigm` which translates to **`Control Content from Contact via Contracts Contextually`**. Sounds intimidating but it is really simple once broken down.


Every information system has:

- **Content**: this is the data you might want to protect i.e. data stored in the system or system(s)

- **Contact**: Entities that want to come in contact with the data (owner of the data, someone granted access by owner, hacker, application) etc.

- **Context**: Information outside the data i.e. dates or times when no one is allowed to update content, ip address of a machine on the network, user browser etc.

- **Contract**: What is a legal or illegal operation when Content, Contact, Context is combined together

- **Control**: The system, processes, tools etc. that deny or allows operations _to_ and _on_ content.

!!! info "So how does this all relate to the **pidentity** mouthful above?"
    You (your application, or organisation) wants to **1. Control** (allow, deny access _to_ or limit actions _on_) **2. Content** (data, information) from **3. Contact** (application, hacker, human)
    via **4. Contract(s)** (combinatory rules) **5. Contextually** (that might use data not stored within the content being controlled).


## Installation

pidentity is a [python](https://python.org) library and as such you need to have Python and PIP installed to be able to use it in your projects.

If you have Python running on your system, then it is extremely easy to install `pidentity` as it comes with 0 code dependencies.

To get started type the command below in your `terminal` or `command prompt`.

```sh
pip install pidentity
```
