import streamlit.components.v1 as components

_component_func = components.declare_component(
    "mic_db_component",
    path="./mic_component/frontend",
)

def mic_db_component():
    return _component_func(default=0.0)
