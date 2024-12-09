import streamlit as st

from frontend.panes.common import at_start
from frontend.state.get_state import get_state
from frontend.utils.models.tournament_options import TournamentOptions

at_start()

state = get_state(user_id=st.session_state.session_id)

st.title("⚔️ Tournament")

# Get current tournament options from state
tournament_options = state.get_tournament_options()

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
        state.set_tournament_options(new_tournament_options)
        st.success(f"{'Mix' if new_tournament_options.mix_tournament else 'Regular'} Tournament started!")  # noqa E501
        st.rerun()

else:
    # If tournament options are already set, display the current tournament type  # noqa E501
    tournament_type = "Mix Tournament" if tournament_options.mix_tournament else "Regular Tournament"  # noqa E501

    st.write(f"Current Tournament Type: **{tournament_type}**")
    players = state.get_players()
    st.write(f"Number of players: **{len(players.players)}**")

    st.divider()

    # Restart tournament functionality
    @st.dialog("Are you sure you want to restart the tournament?")
    def restart_tournament_dialog():
        st.write(
            "**This will reset all scores and games played to zero for all players."  # noqa E501
            " Any ongoing game session will be deleted as well. There will be no way to undo this.**")  # noqa E501
        if st.button("Yes, restart tournament."):
            state.restart_tournament()
            st.success("Tournament restarted.")
            st.rerun()

    if st.button("Restart Tournament"):
        restart_tournament_dialog()

    # End tournament functionality
    @st.dialog("Are you sure you want to delete the tournament?")
    def end_tournament_dialog():
        st.write("**This will permanently delete the tournament and all associated data.**")  # noqa E501
        if st.button("Yes, delete tournament."):
            state.end_tournament()
            st.success("Tournament ended.")
            st.rerun()

    if st.button("End Tournament"):
        end_tournament_dialog()