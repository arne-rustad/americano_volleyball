from frontend.state.base import State
from frontend.state.streamlit import StreamlitState


def get_state() -> State:
    return StreamlitState()
