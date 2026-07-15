import os
import streamlit.components.v1 as components

_component_func = components.declare_component(
    "google_login",
    path=os.path.dirname(os.path.abspath(__file__))
)

def google_login(key=None):
    return _component_func(key=key, default=None)
