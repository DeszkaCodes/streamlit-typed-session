from __future__ import annotations

from collections.abc import Callable, MutableMapping
from typing import Any, TypeVar, final

from streamlit.elements.lib.utils import Key

__all__ = [
    "Unset",
    "StateVar",
    "SessionStateKey",
    "SessionStateValue",
    "SessionStateLike",
    "SessionStateProvider",
]

_T = TypeVar("_T")


@final
class Unset:
    """Used to mark session properties that are not set."""


StateVar = _T | Unset

SessionStateKey = Key
SessionStateValue = Any
SessionStateLike = MutableMapping[SessionStateKey, SessionStateValue]
"""Type that can be used as a session state."""

SessionStateProvider = Callable[[], SessionStateLike]
"""A callable that takes no arguments and returns a SessionStateLike."""
