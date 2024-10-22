import streamlit as st

from americano.player_manager import PlayerManager
from americano.game_session import GameSession
from frontend.config import INFO_ICON, WARNING_ICON
from frontend.utils.state import (
    delete_game_session_state,
    get_game_session_defaults,
    get_game_session_state,
    get_players_from_state,
    update_game_session_defaults,
    update_game_session_state,
    update_players_state,
)

# Initialize or load the game session in session state
game_session = get_game_session_state()
if game_session is None:
    st.title("Start a new game session")
    game_session_defaults = get_game_session_defaults()

    players = get_players_from_state()
    if len(players.players) == 0:
        st.info(
            "You must first add players before you can start a game session.",
            icon=INFO_ICON,
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
        value=game_session_defaults.n_courts,
        key="number_of_courts",
    )
    n_game_points = st.number_input(
        "Number of game points",
        min_value=1,
        value=game_session_defaults.n_game_points,
    )

    n_court_players = []

    # Boolean button allow different number of players across courts
    same_number_of_players = st.checkbox(
        "Same number of players in each team across courts?",
        value=True,
    )

    if same_number_of_players:
        n_court_players = st.number_input(
            "Number of players at each team in all courts",
            min_value=1,
            value=game_session_defaults.n_court_players[0],
            key="n_court_players",
        )
    else:
        for i in range(n_courts):
            if i < len(game_session_defaults.n_court_players):
                default_value = game_session_defaults.n_court_players[i]
            else:
                default_value = game_session_defaults.n_court_players[-1]
            number_input_i = st.number_input(
                f"Number of players at each team in Court {i+1}",
                min_value=1,
                value=default_value,
                key=f"n_court_players_{i}",
            )
            n_court_players.append(number_input_i)

    # Create a new game session if button pressed
    if st.button("Start Game Session"):
        if isinstance(n_court_players, int):
            n_court_players = [n_court_players] * n_courts
        elif not isinstance(n_court_players, list):
            raise ValueError(
                "n_court_players must be either an int or a list."
            )

        total_players_this_session = sum(n_court_players) * 2

        if total_players_this_session > len(players.players):
            st.error(
                f"You have chosen a session that requires {total_players_this_session} players,"  # noqa E501
                f" but you only have {len(players.players)} players."
                " Please add more players or set up a different game session."
            )
            st.stop()

        game_session = GameSession(
            n_courts=n_courts, n_game_points=n_game_points, players=players
        )
        game_session.create_court_sessions(
            n_players_each_team=n_court_players, players=players
        )
        update_game_session_state(game_session=game_session)

        st.success("Game session started!")

        # Update game session defaults
        game_session_defaults.n_courts = n_courts
        game_session_defaults.n_game_points = n_game_points
        game_session_defaults.n_court_players = n_court_players
        update_game_session_defaults(
            game_session_defaults=game_session_defaults
        )

        st.rerun()
else:
    st.title("Manage current game session")

    # Display number of courts and game points
    st.write(f"**Number of courts:** {game_session.n_courts}")
    st.write(f"**Number of game points:** {game_session.n_game_points}")

    # Add end session button to sidebar
    if st.sidebar.button("Delete Game Session"):
        delete_game_session_state()
        st.success("Game session deleted! Player score have NOT been updated.")
        st.rerun()

    # For each court, display the players and score input

    needs_to_rerun_due_to_automatic_points_update = False

    for i, court_session in enumerate(game_session.court_sessions):
        st.header(f"Court {i+1}")

        court_session = game_session.court_sessions[i]

        col_teamA, col_teamB = st.columns(2)
        label_team_A = f"Score for Team A in Court {i+1}"
        label_team_B = f"Score for Team B in Court {i+1}"
        
        with col_teamA:
            st.write(
                f"**Team A:** {', '.join(court_session.teamA)}"
            )
            score_team_A = st.number_input(
                label_team_A,
                min_value=0,
                max_value=game_session.n_game_points,
                value=court_session.score_team_A,
            )

        with col_teamB:
            st.write(
                f"**Team B:** {', '.join(court_session.teamB)}"
            )

            game_session.update_session_score(i, score_team_A=score_team_A)
            score_team_B = st.number_input(
                label_team_B,
                min_value=0,
                max_value=game_session.n_game_points,
                value=court_session.score_team_B,
            )

        match sum(score is None for score in [score_team_A, score_team_B]):
            case 0:
                if score_team_A + score_team_B != game_session.n_game_points:  # noqa E501
                    st.warning(
                        f"The score for team A ({score_team_A}) and team B ({score_team_B})"  # noqa E501
                        f" does not add up to the decided number of game points ({game_session.n_game_points})",  # noqa E501
                        icon=WARNING_ICON,
                    )
            case 1:
                needs_to_rerun_due_to_automatic_points_update = True
                if score_team_A is None:
                    court_session.score_team_A = game_session.n_game_points - score_team_B  # noqa E501
                if score_team_B is None:
                    court_session.score_team_B = game_session.n_game_points - score_team_A  # noqa E501
            case 2:
                pass
            case _:
                raise ValueError("This should never happen")
                  
        update_game_session_state(game_session)
        if needs_to_rerun_due_to_automatic_points_update:
            st.rerun()

        
        

    # Update the scores if button pressed
    if game_session.finished and st.button("Finish Session"):
        players = get_players_from_state()
        player_manager = PlayerManager(player_list=players)
        player_manager.update_player_scores(game_session.court_sessions, resting_points=game_session.n_game_points / 2)  # noqa E501
        update_players_state(players)
        delete_game_session_state()
        st.success("Session finished! Player scores updated.")
        st.rerun()
