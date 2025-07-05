from __future__ import annotations

import sys
import types
import typing
import warnings
from collections.abc import Callable, Mapping

import typing_extensions

from streamlit_typed_session.descriptors import DefaultSessionVariableDescriptor, SessionVariableDescriptor
from streamlit_typed_session.mytypes import (
    SessionStateLike,
    SessionStateProvider,
    Unset,
    UnsetType,
)
from streamlit_typed_session.providers import streamlit_session_provider

_IGNORED_TYPES: tuple[type, ...] = (
    types.FunctionType,
    types.BuiltinFunctionType,
    types.BuiltinMethodType,
    property,
    classmethod,
    staticmethod,
    typing_extensions.TypeAliasType,
)

if sys.version_info >= (3, 12):
    _IGNORED_TYPES = (*_IGNORED_TYPES, typing.TypeAliasType)


class SessionModelMetaclass(type):
    def __new__(
        cls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, typing.Any],
        *,
        mute_warnings: bool = False,
        state: SessionStateLike | SessionStateProvider = streamlit_session_provider,
    ) -> typing.Self:
        if isinstance(state, Callable):
            state = state()

        namespace["__state__"] = state

        descriptors: dict[str, SessionVariableDescriptor[typing.Any]] = {}
        namespace["__session_descriptors__"] = descriptors

        annotations = typing.cast("dict[str, typing.Any]", namespace.get("__annotations__", {}))

        for attribute, raw_annotation in annotations.items():
            if attribute.startswith("_"):  # Skip private attributes
                continue
            session_key = f"__{namespace['__module__']}.{namespace['__qualname__']}.{attribute}__"

            annotation = _parse_annotation(raw_annotation)
            is_type_state_var = cls._is_type_state_var(annotation)
            if attribute in namespace and is_type_state_var and not mute_warnings:
                warnings.warn(
                    f"Attribute '{attribute}' defines a default value but also has type-hint for '{Unset.__name__}'."
                    " Session variables with default values will never be unset so this type-hint is not required."
                    f" To suppress this warning remove the '{Unset.__name__}' type annotation or"
                    f" set 'no_warnings' to 'True' when inheriting.",
                    stacklevel=3,
                )
            elif attribute not in namespace and not is_type_state_var and not mute_warnings:
                warnings.warn(
                    f"Attribute '{attribute}' does not have '{Unset.__name__}' in its type annotation"
                    " and does not have a default value either."
                    " This causes issues with type-checkers. "
                    f" To suppress this warning add '{Unset.__name__}' into the type annotation or"
                    f" set 'no_warnings' to 'True' when inheriting.",
                    stacklevel=3,
                )

            descriptor = (
                DefaultSessionVariableDescriptor[typing.Any](state, session_key, default=namespace[attribute])
                if attribute in namespace
                else SessionVariableDescriptor[typing.Any](state, session_key)
            )
            namespace[attribute] = descriptor
            descriptors[attribute] = descriptor

        for attribute, value in namespace.items():
            if attribute.startswith("_"):  # Skip private attributes
                continue

            if attribute in descriptors:
                continue

            if any(isinstance(value, t) for t in _IGNORED_TYPES):
                continue

            session_key = f"__{namespace['__module__']}.{namespace['__qualname__']}.{attribute}__"

            descriptor = DefaultSessionVariableDescriptor(state, session_key, default=value)
            namespace[attribute] = descriptor
            descriptors[attribute] = descriptor

        return super().__new__(cls, name, bases, namespace)


def _is_type_state_var(inspected: type | types.UnionType) -> bool:
    origin = typing.get_origin(inspected)
    if origin is not typing.Union and origin is not types.UnionType:
        return False

    return UnsetType in typing.get_args(inspected)


def _parse_annotation(annotation: object) -> typing.Any:
    if isinstance(annotation, str):
        frame = sys._getframe(1)  # noqa: SLF001
        annotation = _eval_type(
            _make_forward_ref(annotation, is_argument=False, is_class=True),
            frame.f_globals,
            frame.f_locals,
        )

    return annotation


def _eval_type(
    t: typing.ForwardRef | types.GenericAlias | types.UnionType,
    globalns: dict[str, typing.Any] | None,
    localns: Mapping[str, typing.Any] | None,
    type_params: object = (),
) -> typing.Any:
    # TODO: fix type_params
    if sys.version_info >= (3, 13):
        return typing._eval_type(t, globalns, localns, type_params)  # noqa: SLF001

    return typing._eval_type(t, globalns, localns)  # noqa: SLF001


if (3, 10) <= sys.version_info < (3, 10, 1):

    def _make_forward_ref(
        arg: object,
        is_argument: bool = True,
        *,
        is_class: bool = False,  # noqa: ARG001
    ) -> typing.ForwardRef:
        """This function has been made from the Pydantic implementation."""
        return typing.ForwardRef(arg, is_argument)

else:
    _make_forward_ref = typing.ForwardRef
