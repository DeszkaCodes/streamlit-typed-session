from __future__ import annotations

import sys
from collections.abc import Callable
from typing import Generic, NoReturn, TypeVar, overload

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


from streamlit_typed_session.mytypes import SessionStateLike, Unset

__all__ = ["SessionVariableDescriptor", "DefaultSessionVariableDescriptor"]

_TR = TypeVar("_TR")


class SessionVariableDescriptor(Generic[_TR]):
    """Descriptor that manipulates a session state."""

    @property
    def key(self) -> str:
        return self._key

    def __init__(
        self,
        session_state: SessionStateLike,
        key: str,
    ):
        self._key: str = key
        self._session_state: SessionStateLike = session_state

    def __set_name__(self, owner: type, name: str) -> None:
        self.__name__ = name

    @overload
    def __get__(self, instance: None, type: type) -> NoReturn: ...

    @overload
    def __get__(self, instance: object, type: type) -> _TR | type[Unset]: ...

    @overload
    def __get__(
        self,
        instance: object | None,
        type: type,
    ) -> NoReturn | _TR | type[Unset]: ...

    def __get__(
        self,
        instance: object | None,
        type: type,
    ) -> NoReturn | _TR | type[Unset]:
        if instance is None:
            raise AttributeError(f"type object '{type.__name__}' has no attribute '{self.__name__}'")

        if self._key not in self._session_state:
            return Unset

        return self._session_state[self._key]

    def __set__(self, instance: object, value: _TR) -> None:
        self._session_state[self._key] = value

    def __delete__(self, instance: object) -> None:
        if self._key in self._session_state:
            del self._session_state[self._key]


class DefaultSessionVariableDescriptor(SessionVariableDescriptor[_TR]):
    @property
    def default(self) -> _TR:
        return self._default

    @overload
    def __init__(self, session_state: SessionStateLike, key: str, *, default: _TR) -> None: ...
    @overload
    def __init__(self, session_state: SessionStateLike, key: str, *, default_factory: Callable[[], _TR]) -> None: ...
    @overload
    def __init__(
        self,
        session_state: SessionStateLike,
        key: str,
        *,
        default: _TR | type[Unset] = Unset,
        default_factory: Callable[[], _TR] | type[Unset] = Unset,
    ) -> None: ...

    def __init__(
        self,
        session_state: SessionStateLike,
        key: str,
        *,
        default: _TR | type[Unset] = Unset,
        default_factory: Callable[[], _TR] | type[Unset] = Unset,
    ) -> None:
        if (default is Unset and default_factory is Unset) or (default is not Unset and default_factory is not Unset):
            raise ValueError("either 'default' or 'default_factory' must be set but not both")

        if default_factory is not Unset:
            default = default_factory()
        else:
            assert default is not Unset

        super().__init__(session_state, key)

        self._default: _TR = default

    @overload
    def __get__(self, instance: None, type: type) -> NoReturn: ...

    @overload
    def __get__(self, instance: object, type: type) -> _TR: ...

    @overload
    def __get__(
        self,
        instance: object | None,
        type: type,
    ) -> NoReturn | _TR: ...

    @override
    def __get__(
        self,
        instance: object | None,
        type: type,
    ) -> NoReturn | _TR:
        if self._key not in self._session_state:
            self._session_state[self._key] = self._default

        value = super().__get__(instance, type)
        assert value is not Unset
        return value
