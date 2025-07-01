from __future__ import annotations

from streamlit_typed_session.mytypes import SessionStateLike

__all__ = ["streamlit_session_provider"]


def streamlit_session_provider() -> SessionStateLike:
    """The default provider that returns Streamlit's session state.

    Returns:
        SessionStateLike: The sesion state of Streamlit.
    """
    import streamlit

    return streamlit.session_state
