from __future__ import annotations

import streamlit as st

from streamlit_typed_session.bases import SessionBase
from streamlit_typed_session.mytypes import StateVar, Unset


class SessionModel(SessionBase):
    number: StateVar[int]


session_state = SessionModel()

st.write(f"Value: `{session_state.number}`")

new_number = st.number_input(
    "Number",
    value=session_state.number if session_state.number is not Unset else 0,
)

if st.button("Set"):
    session_state.number = new_number
    st.rerun()

if st.button("Delete"):
    del session_state.number
    st.rerun()

st.divider()

st.write(dict(st.session_state))
