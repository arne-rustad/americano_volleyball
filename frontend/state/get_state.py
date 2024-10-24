from frontend.utils.state.base import State
from frontend.utils.state.streamlit import StreamlitState


def get_state() -> State:
    return StreamlitState()
