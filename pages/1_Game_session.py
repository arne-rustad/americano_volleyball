from americano.sessions import GameSession
from americano.players import PlayerList
import streamlit as st


if st.session_state.get("game_session_defaults") is None:
    game_session_defaults = {
        "n_courts": 3,
        "n_game_points": 21,
        "n_court_players": [4, 4, 4]
    }
    st.session_state["game_session_defaults"] = game_session_defaults
else:
    game_session_defaults = st.session_state["game_session_defaults"]


if st.session_state.get("players") is None:
    st.write("You must first add players")
    st.stop()

# Initialize or load the game session in session state
if st.session_state.get("game_session") is None:  # noqa E501

    players = PlayerList.model_validate_json(st.session_state["players"])

    # Write current players
    st.write(f"**Current players:** {', '.join([player.name for player in players.players])}")  # noqa E501

    # Take the number of courts and game points as input
    n_courts = st.number_input(
        "Number of courts",
        min_value=1,
        value=game_session_defaults["n_courts"],
        key="number_of_courts"
    )  # noqa E501
    n_game_points = st.number_input("Number of game points", min_value=1, value=game_session_defaults["n_game_points"])  # noqa E501

    n_court_players = []
    for i in range(n_courts):
        if i < len(game_session_defaults["n_court_players"]):
            default_value = game_session_defaults["n_court_players"][i]
        else:
            default_value = 4
        number_input_i = st.number_input(
            f"Number of players at each team in Court {i+1}",
            min_value=1,
            value=default_value,
            key=f"n_court_players_{i}"
        )  # noqa E501
        n_court_players.append(number_input_i)

    # Create a new game session if button pressed
    if st.button("Start Game Session"):
        game_session = GameSession(
            n_courts=n_courts,
            n_game_points=n_game_points,
            players=players
        )
        game_session.create_court_sessions(n_court_players)
        st.session_state["game_session"] = game_session.model_dump_json()

        st.success("Game session started!")

        # Update game session defaults
        game_session_defaults["n_courts"] = n_courts
        game_session_defaults["n_game_points"] = n_game_points
        game_session_defaults["n_court_players"] = n_court_players
        st.session_state["game_session_defaults"] = game_session_defaults

        st.rerun()
else:
    game_session = GameSession.model_validate_json(st.session_state["game_session"])  # noqa E501
    # Hack until I rewrite add_score_to_players and separate PlayerList from GameSession  # noqa E501
    n_court_players = [s.n_players_each_team for s in game_session.court_sessions]  # noqa E501
    score_team_A_list = [s.score_team_A for s in game_session.court_sessions]  # noqa E501
    game_session.create_court_sessions(n_court_players)
    for i, score in enumerate(score_team_A_list):
        game_session.update_session_score(i, score_team_A=score)

    # Display number of courts and game points
    st.write(f"**Number of courts:** {game_session.n_courts}")  # noqa E501
    st.write(f"**Number of game points:** {game_session.n_game_points}")  # noqa E501

    # Add end session button to sidebar
    if st.sidebar.button("End Session"):
        del st.session_state["game_session"]
        st.success("Game session ended!")
        st.rerun()

    # For each court, display the players and score input

    court_scores_team_A = []

    for i, court_session in enumerate(game_session.court_sessions):  # noqa E501
        st.header(f"Court {i+1}")
        st.write(f"Team A: {', '.join([player.name for player in court_session.teamA])}")  # noqa E501
        st.write(f"Team B: {', '.join([player.name for player in court_session.teamB])}")  # noqa E501

        court_session = game_session.court_sessions[i]

        score_team_A = st.number_input(
            f"**Score for Team A in Court {i+1}**",
            min_value=0,
            max_value=game_session.n_game_points,
            value=court_session.score_team_A if court_session.score_team_A else None  # noqa E501
        )  # noqa E501
        court_scores_team_A.append(score_team_A)
        if score_team_A is not None:
            game_session.update_session_score(i, score_team_A=score_team_A)  # noqa E501
            st.session_state["game_session"] = game_session.model_dump_json()  # noqa E501

            score_team_B = game_session.n_game_points - score_team_A  # noqa E501
            st.write(f"**Score for Team B in Court {i+1}:** {score_team_B}")

    # Update the scores if button pressed
    if game_session.finished:
        if st.button("Finish Session"):
            game_session.add_score_to_players()  # noqa E501
            st.session_state["players"] = game_session.players.model_dump_json()  # noqa E501
            del st.session_state["game_session"]
            st.success("Session finished!")
            st.rerun()
