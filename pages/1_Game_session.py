from americano.sessions import GameSession
from americano.players import PlayerList
import streamlit as st

if "players" not in st.session_state:
    st.write("You must first add players")
    st.stop()

# Initialize or load the game session in session state
if "game_session" not in st.session_state:  # noqa E501

    players = PlayerList.parse_raw(st.session_state["players"])

    # Write current players
    st.write(f"**Current players:** {', '.join([player.name for player in players.players])}")  # noqa E501

    # Take the number of courts and game points as input
    n_courts = st.number_input("Number of courts", min_value=1, value=3)
    n_game_points = st.number_input("Number of game points", min_value=1, value=21)  # noqa E501

    n_court_players = []
    for i in range(n_courts):
        n_court_players.append(st.number_input(f"Number of players in Court {i+1}", min_value=1, value=4))  # noqa E501

    # Create a new game session if button pressed
    if st.button("Start Game Session"):
        st.session_state["game_session"] = GameSession(
            n_courts=n_courts,
            n_game_points=n_game_points,
            players=players
        )
        st.session_state["game_session"].create_court_sessions(n_court_players)
        st.success("Game session started!")
        st.rerun()
else:
    # Display number of courts and game points
    st.write(f"**Number of courts:** {st.session_state['game_session'].n_courts}")  # noqa E501
    st.write(f"**Number of game points:** {st.session_state['game_session'].n_game_points}")  # noqa E501

    # Add end session button to sidebar
    if st.sidebar.button("End Session"):
        del st.session_state["game_session"]
        st.success("Game session ended!")
        st.rerun()

    # For each court, display the players and score input

    court_scores_team_A = []

    for i, court_session in enumerate(st.session_state["game_session"].court_sessions):  # noqa E501
        st.header(f"Court {i+1}")
        st.write(f"Team A: {', '.join([player.name for player in court_session.teamA])}")  # noqa E501
        st.write(f"Team B: {', '.join([player.name for player in court_session.teamB])}")  # noqa E501

        score_team_A = st.number_input(
            f"**Score for Team A in Court {i+1}**",
            min_value=0,
            max_value=st.session_state["game_session"].n_game_points,
            value=None
        )  # noqa E501
        court_scores_team_A.append(score_team_A)
        if score_team_A is not None:
            st.session_state["game_session"].update_session_score(i, score_team_A=score_team_A)  # noqa E501
            score_team_B = st.session_state["game_session"].n_game_points - score_team_A  # noqa E501
            st.write(f"**Score for Team B in Court {i+1}:** {score_team_B}")

    # Update the scores if button pressed
    if st.session_state["game_session"].finished:
        if st.button("Finish Session"):
            st.session_state["game_session"].add_score_to_players()  # noqa E501
            st.session_state["players"] = st.session_state["game_session"].players.model_dump_json()  # noqa E501
            st.session_state["game_session"] = None
            st.success("Session finished!")
            st.rerun()
