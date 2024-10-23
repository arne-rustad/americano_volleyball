import streamlit as st

from frontend.config import INFO_ICON, SUCCESS_ICON
from frontend.utils.models.tournament_options import TournamentOptions
from frontend.utils.state import (
    end_tournament,
    get_players_from_state,
    get_tournament_options,
    update_tournament_options,
)

if st.session_state.get("end_tournament_question"):
    match st.session_state["end_tournament_question"]:
        case "INITIATED":
            st.session_state["end_tournament_question"] = "ASKING_CONFIRMATION"
        case "ASKING_CONFIRMATION":
            st.session_state["end_tournament_question"] = "CHECKING_IF_USER_WANTS_TO_END_TOURNAMENT"  # noqa E501
        case "DON'T END TOURNAMENT":
            st.info("Tournament not ended.", icon=INFO_ICON)
            del st.session_state["end_tournament_question"]
        case "END TOURNAMENT":
            st.success("Tournament ended.", icon=SUCCESS_ICON)
            del st.session_state["end_tournament_question"]
        case "CHECKING_IF_USER_WANTS_TO_END_TOURNAMENT":
            del st.session_state["end_tournament_question"]
        case _:
            raise ValueError("Invalid end tournament question")

st.title("⚔️ Tournament")

# Get current tournament options from state
tournament_options = get_tournament_options()

if tournament_options is None:
    # If no tournament options are set, allow the user to choose
    st.write("Choose the tournament type:")
    is_mix_tournament = st.radio(
        "Tournament Type",
        options=["Regular Tournament", "Mix Tournament"],
        format_func=lambda x: "Mix Tournament" if x == "Mix Tournament" else "Regular Tournament",  # noqa E501
    )

    if st.button("Start Tournament"):
        new_tournament_options = TournamentOptions(mix_tournament=(is_mix_tournament == "Mix Tournament"))  # noqa E501
        update_tournament_options(new_tournament_options)
        st.success(f"{'Mix' if new_tournament_options.mix_tournament else 'Regular'} Tournament started!")  # noqa E501
        st.rerun()

else:
    # If tournament options are already set, display the current tournament type
    tournament_type = "Mix Tournament" if tournament_options.mix_tournament else "Regular Tournament"  # noqa E501

    st.write(f"Current Tournament Type: **{tournament_type}**")
    players = get_players_from_state()
    st.write(f"Number of players: **{len(players.players)}**")

    st.header("End tournament")
    with st.sidebar:
    @st.dialog("Are you sure you want to delete the game session?")
        def end_tournament_dialog():
            st.write("**This will permanently delete the tournament and all associated data**")  # noqa E501
            if st.button("Yes, delete tournament"):
                end_tournament()
                st.success("Tournament ended.")

    if st.session_state.get("end_tournament_question") is None:
        if st.button("End Tournament"):
            st.session_state["end_tournament_question"] = "INITIATED"
            st.rerun()
    else:
        # Create yes no with inside format
        with st.form("end_tournament_form"):
            end_tournament_confirmation = st.radio("Are you sure you want to end the tournament? **This action cannot be undone!**", options=["Yes", "No"])  # noqa E501
        
            submitted = st.form_submit_button("Submit")
            
            if submitted:
                if end_tournament_confirmation == "Yes":
                    end_tournament()
                    st.session_state["end_tournament_question"] = "END TOURNAMENT"  # noqa E501
                else:
                    st.session_state["end_tournament_question"] = "DON'T END TOURNAMENT"  # noqa E501
                st.rerun()
