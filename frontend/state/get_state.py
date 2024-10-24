from frontend.state.base import State
from frontend.state.firebase import FirestoreState


def get_state(user_id: str) -> State:
    return FirestoreState(user_id=user_id)
