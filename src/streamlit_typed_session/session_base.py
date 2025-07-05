from __future__ import annotations

import types
import typing

from streamlit_typed_session._metaclass import SessionModelMetaclass

if typing.TYPE_CHECKING:
    from streamlit_typed_session.descriptors import SessionVariableDescriptor
    from streamlit_typed_session.mytypes import (
        SessionStateKey,
        SessionStateLike,
        SessionStateValue,
    )

__all__ = ["SessionBase"]


class SessionBase(metaclass=SessionModelMetaclass):
    __session_descriptors__: typing.ClassVar[dict[str, SessionVariableDescriptor[typing.Any]]]
    __state__: typing.ClassVar[SessionStateLike]

    @typing.final
    def __init__(self) -> None: ...

    @classmethod
    def get_descriptors(
        cls,
    ) -> list[SessionVariableDescriptor[typing.Any]]:
        return list(cls.__session_descriptors__.values())

    @classmethod
    def get_descriptor(cls, name: str) -> SessionVariableDescriptor[typing.Any]:
        if name not in cls.__session_descriptors__:
            msg = f"attribute '{name}' is not a session variable"
            raise AttributeError(msg)

        return cls.__session_descriptors__[name]

    @typing.overload
    @classmethod
    def get_state(
        cls,
    ) -> types.MappingProxyType[SessionStateKey, SessionStateValue]: ...

    @typing.overload
    @classmethod
    def get_state(cls, read_only: typing.Literal[False]) -> SessionStateLike: ...

    @typing.overload
    @classmethod
    def get_state(
        cls, *, read_only: bool = True
    ) -> types.MappingProxyType[SessionStateKey, SessionStateValue] | SessionStateLike: ...

    @classmethod
    def get_state(
        cls, *, read_only: bool = True
    ) -> types.MappingProxyType[SessionStateKey, SessionStateValue] | SessionStateLike:
        if read_only:
            return types.MappingProxyType(cls.__state__)

        return cls.__state__
