import streamlit as st

from americano.game_session import GameSession
from americano.player_manager import PlayerManager
from frontend.config import INFO_ICON, WARNING_ICON
from frontend.panes.common import at_start
from frontend.state.get_state import State, get_state

at_start()

state = get_state(user_id=st.session_state.session_id)

tournament_options = state.get_tournament_options()
if tournament_options is None:
    st.info("You must first start a tournament.", icon=INFO_ICON)
    st.stop()

# Initialize or load the game session in session state
game_session = state.get_game_session()
if game_session is None:
    st.title("Start a new game session")
    game_session_defaults = state.get_defaults()

    players = state.get_players()
    if len(players.players) == 0:
        st.info(
            "You must first add players before you can start a game session.",
            icon=INFO_ICON,
        )
        st.stop()

    # Write current players
    st.write(f"**Number of players available:** {len(players.players)}")

    # Take the number of courts and game points as input
    n_courts = st.number_input(
        "Number of courts",
        min_value=1,
        value=game_session_defaults.n_courts,
        key="number_of_courts",
    )
    container_n_game_points = st.empty()
    with container_n_game_points:
        n_game_points = st.number_input(
            "Number of game points",
            min_value=1,
            value=game_session_defaults.n_game_points,
            help="The total number of points that should be played in each court. The game is finished when 'points team A' + 'points team B' = 'number of game points'.",  # noqa E501
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

    with st.expander("Advanced options"):
        use_default_game_points = st.checkbox(
            label="Use default game points",
            help="If checked, the game session will expect that the total points of both teams on a court sums up to the decided number of game points.",  # noqa E501
            value=game_session_defaults.use_default_game_points,
        )
        if not use_default_game_points:
            container_n_game_points.empty()

        override_resting_points = st.checkbox(
            label="Manually override resting points",
            help="If unchecked, resting players will receive the number of game points divided by two.",  # noqa E501
            value=game_session_defaults.override_resting_points,
        )
        if override_resting_points:
            resting_points_manual = st.number_input(
                "Resting points",
                min_value=0,
                value=game_session_defaults.resting_points_manual,
            )
        else:
            if use_default_game_points:
                st.info(
                    icon=INFO_ICON,
                    body="Since you have chosen to use default game points, resting points will be set to **half of the game points** by default unless you override manually."  # noqa E501
                )
            else:
                st.info(
                    icon=INFO_ICON,
                    body="Since you have chosen to not provide default game points, resting points will be set to **0** by default unless you override manually."  # noqa E501
                )
        
        allow_negative_player_scores = st.checkbox(
            label="Allow negative player scores",
            help="If checked, players can get negative scores.",
            value=game_session_defaults.allow_negative_player_scores,
        )

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
        
        default_resting_points = n_game_points / 2 if use_default_game_points else 0  # noqa E501
        game_session = GameSession(
            n_courts=n_courts,
            n_game_points=n_game_points if use_default_game_points else None,
            resting_points=resting_points_manual if override_resting_points else default_resting_points,  # noqa E501
            allow_negative_player_scores=allow_negative_player_scores,
        )
        game_session.create_court_sessions(
            n_players_each_team=n_court_players,
            players=players,
            mix_tournament=tournament_options.mix_tournament,
        )
        state.set_game_session(game_session=game_session)

        st.success("Game session started!")

        # Update game session defaults
        game_session_defaults.n_courts = n_courts
        game_session_defaults.n_game_points = n_game_points
        game_session_defaults.n_court_players = n_court_players
        game_session_defaults.use_default_game_points = use_default_game_points
        game_session_defaults.override_resting_points = override_resting_points
        game_session_defaults.resting_points_manual = resting_points_manual if override_resting_points else 0  # noqa E501
        game_session_defaults.allow_negative_player_scores = allow_negative_player_scores  # noqa E501
        state.set_defaults(defaults=game_session_defaults)
        st.rerun()
else:
    st.title("Manage current game session")

    # Display number of courts and game points
    st.write(f"**Number of courts:** {game_session.n_courts}")
    if game_session.n_game_points is not None:
        st.write(f"**Number of game points:** {game_session.n_game_points}")
    st.write(f"**Resting points for players not playing:** {game_session.resting_points}")  # noqa E501

    # Add end session button to sidebar
    with st.sidebar:

        @st.dialog("Are you sure you want to delete the game session?")
        def delete_game_session_dialog():
            if st.button("Yes, delete game session"):
                state.delete_game_session()
                st.success(
                    "Game session deleted! Player score have NOT been updated."
                )
                st.rerun()

        if st.button("Delete Game Session"):
            delete_game_session_dialog()

    # For each court, display the players and score input

    # needs_to_rerun_due_to_automatic_points_update = False

    for i, court_session in enumerate(game_session.court_sessions):
        st.header(f"Court {i+1}")

        court_session = game_session.court_sessions[i]

        col_teamA, col_score_teamA, col_score_teamB, col_teamB = st.columns(
            [1, 1, 1, 1]
        )  # noqa E501
        label_team_A = f"Score for Team A in Court {i+1}"
        label_team_B = f"Score for Team B in Court {i+1}"

        def update_score_for_team(
            state: State, court_index=i, score_team_A=None, score_team_B=None
        ):  # noqa E501
            game_session.update_session_score(
                court_index=court_index,
                score_team_A=score_team_A,
                score_team_B=score_team_B,
            )
            state.set_game_session(game_session)

        with col_teamA:
            st.write(f"**Team A:** {', '.join(court_session.teamA)}")
        with col_score_teamA:
            score_team_A = st.number_input(
                label_team_A,
                key=label_team_A,
                min_value=None if game_session.allow_negative_player_scores else 0,  # noqa E501
                max_value=game_session.n_game_points,
                value=court_session.score_team_A,
                placeholder=label_team_A,
                label_visibility="collapsed",
                on_change=lambda index=i,
                label_A=label_team_A: update_score_for_team(
                    state=state,
                    court_index=index,
                    score_team_A=st.session_state[label_A],
                ),
            )

        with col_teamB:
            st.write(f"**Team B:** {', '.join(court_session.teamB)}")
        with col_score_teamB:
            score_team_B = st.number_input(
                label_team_B,
                key=label_team_B,
                min_value=None if game_session.allow_negative_player_scores else 0,  # noqa E501
                max_value=game_session.n_game_points,
                value=court_session.score_team_B,
                placeholder=label_team_B,
                label_visibility="collapsed",
                on_change=lambda index=i,
                label_B=label_team_B: update_score_for_team(
                    state=state,
                    court_index=index,
                    score_team_B=st.session_state[label_B],
                ),
            )

        if (
            score_team_A is not None
            and score_team_B is not None
            and game_session.n_game_points is not None
            and score_team_A + score_team_B != game_session.n_game_points
        ):
            st.warning(
                f"The score for team A ({score_team_A}) and team B ({score_team_B})"  # noqa E501
                f" does not add up to the decided number of game points ({game_session.n_game_points})",  # noqa E501
                icon=WARNING_ICON,
            )

    # Update the scores if button pressed
    if game_session.finished and st.button("Finish Session"):
        players = state.get_players()
        player_manager = PlayerManager(player_list=players)
        player_manager.update_player_scores(
            game_session.court_sessions,
            resting_points=game_session.resting_points,
        )
        state.set_players(players)
        state.delete_game_session()
        st.success("Session finished! Player scores updated.")
        st.rerun()
