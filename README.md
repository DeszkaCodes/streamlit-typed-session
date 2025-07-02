# Streamlit Typed Session

This package is made for people who like the safety of Python static type-checkers but also have to work with Streamlit at the same time.

**Caution** this project is under heavy development.

## Guide

The current main API was inspired by `pydantic-settings`.

To start you just need to import `streamlit_typed_session.SessionBase` and `streamlit_typed_session.StateVar` and declare a class as in the example below.

```py
from streamlit_typed_session import SessionBase, StateVar


class SessionModel(SessionBase):
    number: StateVar[int]

session_state = SessionModel()
```

After this you can use `session_state` as a normal class.

Under the hood the attributes of `SessionModel` are turned into descriptors, that modify the underlying `st.session_state`.

For a more detailed example check [`scripts/streamlit_test.py`](./scripts/streamlit_test.py)

### Why `StateVar`?

`StateVar` is a "syntactic sugar", its underlying type is `T | UnsetType`. Every attribute that does not have a default value _should_ have `UnsetType` in its type hints. This is required as if the attribute is not present in the underlying session state (and does not have a default value) they will return `Unset` instead of raising an exception. By providing `UnsetType` as a type hint you can rely on static type-checkers to warn you if an attribute might be unset.
