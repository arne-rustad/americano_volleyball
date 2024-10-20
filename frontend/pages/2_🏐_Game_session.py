import streamlit as st

from americano.players import PlayerList
from americano.sessions import GameSession

if st.session_state.get("game_session_defaults") is None:
    game_session_defaults = {
        "n_courts": 3,
        "n_game_points": 21,
        "n_court_players": [4, 4, 4],
    }
    st.session_state["game_session_defaults"] = game_session_defaults
else:
    game_session_defaults = st.session_state["game_session_defaults"]

# Initialize or load the game session in session state
if st.session_state.get("game_session") is None:
    players = PlayerList.model_validate_json(st.session_state["players"])
    if len(players.players) == 0:
        st.write(
            "You must first add players before you can start a game session."
        )
        st.stop()

    # Write current players
    st.write(
        f"**Current players:** {', '.join([player.name for player in players.players])}"  # noqa E501
    )

    # Take the number of courts and game points as input
    n_courts = st.number_input(
        "Number of courts",
        min_value=1,
        value=game_session_defaults["n_courts"],
        key="number_of_courts",
    )
    n_game_points = st.number_input(
        "Number of game points",
        min_value=1,
        value=game_session_defaults["n_game_points"],
    )

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
            key=f"n_court_players_{i}",
        )
        n_court_players.append(number_input_i)

    # Create a new game session if button pressed
    if st.button("Start Game Session"):
        total_players_this_session = sum(n_court_players) * 2
        if total_players_this_session > len(players.players):
            st.error(
                f"You have chosen a session that requires {total_players_this_session} players,"  # noqa E501
                " but you only have {len(players.players)} players."
                " Please add more players or set up a different game session."
            )
            st.stop()

        game_session = GameSession(
            n_courts=n_courts, n_game_points=n_game_points, players=players
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
    game_session = GameSession.model_validate_json(
        st.session_state["game_session"]
    )
    # Hack until I rewrite add_score_to_players and separate PlayerList from GameSession  # noqa E501
    n_court_players = [
        s.n_players_each_team for s in game_session.court_sessions
    ]
    score_team_A_list = [s.score_team_A for s in game_session.court_sessions]
    game_session.create_court_sessions(n_court_players)
    for i, score in enumerate(score_team_A_list):
        game_session.update_session_score(i, score_team_A=score)

    # Display number of courts and game points
    st.write(f"**Number of courts:** {game_session.n_courts}")
    st.write(f"**Number of game points:** {game_session.n_game_points}")

    # Add end session button to sidebar
    if st.sidebar.button("End Session"):
        del st.session_state["game_session"]
        st.success("Game session ended!")
        st.rerun()

    # For each court, display the players and score input

    court_scores_team_A = []

    for i, court_session in enumerate(game_session.court_sessions):
        st.header(f"Court {i+1}")
        st.write(
            f"Team A: {', '.join([player.name for player in court_session.teamA])}"  # noqa E501
        )
        st.write(
            f"Team B: {', '.join([player.name for player in court_session.teamB])}"  # noqa E501
        )

        court_session = game_session.court_sessions[i]

        score_team_A = st.number_input(
            f"**Score for Team A in Court {i+1}**",
            min_value=0,
            max_value=game_session.n_game_points,
            value=court_session.score_team_A
            if court_session.score_team_A
            else None,
        )
        court_scores_team_A.append(score_team_A)
        if score_team_A is not None:
            game_session.update_session_score(i, score_team_A=score_team_A)
            st.session_state["game_session"] = game_session.model_dump_json()

            score_team_B = game_session.n_game_points - score_team_A
            st.write(f"**Score for Team B in Court {i+1}:** {score_team_B}")

    # Update the scores if button pressed
    if game_session.finished and st.button("Finish Session"):
        players = 
        players.add_score_to_players()
        st.session_state["players"] = (
            game_session.players.model_dump_json()
        )
        del st.session_state["game_session"]
        st.success("Session finished!")
        st.rerun()
