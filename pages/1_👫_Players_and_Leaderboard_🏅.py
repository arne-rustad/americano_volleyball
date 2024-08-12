import os
import streamlit as st
from americano.players import PlayerList
from americano.sessions import GameSession
from dotenv import load_dotenv

load_dotenv()


def update_player_session_state(players):
    st.session_state["players"] = players.model_dump_json()
    game_session_state = st.session_state.get("game_session")
    if game_session_state is not None:
        game_session = GameSession.model_validate_json(game_session_state)
        game_session.players = players
        st.session_state["game_session"] = game_session.model_dump_json()


if os.getenv("SAVED_PLAYERS"):
    SAVED_PLAYERS = os.getenv("SAVED_PLAYERS").split(",", )
    SAVED_PLAYERS = [player.strip() for player in SAVED_PLAYERS]
else:
    SAVED_PLAYERS = []

st.title("Americano Volleyball app")

# Initialize or load the player list in session state.
# Use from game_session if game_session is active, else from players.
if st.session_state.get("game_session") is not None:
    players = GameSession.model_validate_json(st.session_state["game_session"]).players  # noqa E501
else:
    if st.session_state.get("players") is None:
        st.session_state["players"] = PlayerList().model_dump_json()
    players = PlayerList.model_validate_json(st.session_state["players"])

if st.session_state.get("reset_confirmation") is None or st.session_state.get("reset_confirmation") is False:  # noqa E501
    reset_confirmation = False
else:
    reset_confirmation = True
    st.session_state["reset_confirmation"] = False

# Display saved players list in sidebar with a button to load them
if SAVED_PLAYERS:
    saved_players_loaded = 0
    st.sidebar.header("Saved players:")
    for i, player_name in enumerate(SAVED_PLAYERS):
        if player_name in players.get_names():  # noqa E501
            saved_players_loaded += 1
        else:
            if st.sidebar.button(f"Load {player_name}"):
                players.add_player(player_name)
                update_player_session_state(players)
                st.success(f"Player {player_name} loaded!")
                st.rerun()

    # Load all saved players
    if saved_players_loaded < len(SAVED_PLAYERS):
        st.sidebar.divider()
        if st.sidebar.button("Load all saved players"):
            for player_name in SAVED_PLAYERS:
                if player_name not in players.get_names():
                    players.add_player(player_name)
            update_player_session_state(players)
            st.rerun()
        st.sidebar.divider()
    else:
        st.sidebar.write("All saved players already loaded!")
        st.sidebar.divider()

# Add Player
new_player_name = st.text_input("Add a new player")
if st.button("Add Player"):
    try:
        players.add_player(new_player_name)
        update_player_session_state(players)
        st.success(f"Player {new_player_name} added!")
    except ValueError as e:
        st.error(e)

# Reset button in sidebar
if st.sidebar.button("Reset"):
    st.session_state["reset_confirmation"] = True
    reset_confirmation = True

if reset_confirmation:
    # Are you sure message popup
    st.sidebar.write("Are you sure you want to reset? Press either Yes or No")
    if st.sidebar.button("Yes"):
        del st.session_state["players"]
        if st.session_state.get("game_session"):
            del st.session_state["game_session"]
        st.rerun()
    if st.sidebar.button("No"):
        st.rerun()


# Display players based on pandas dataframe
st.header("List of players:")
if players.players:
    st.dataframe(
        players.to_pandas(),
        width=1000,
        height=1000
    )
else:
    st.write("No players added yet")
    st.stop()

if "game_session" in st.session_state:
    st.write("Game session is active. End the session to remove players.")
else:
    # Remove player by name
    remove_player_name = st.selectbox("Select player to remove", players.get_names())  # noqa E501

    if st.button("Remove Player"):
        player = players.remove_player_by_name(remove_player_name)  # noqa E501
        if player:
            update_player_session_state(players)
            st.success(f"Player {remove_player_name} removed!")
            st.rerun()
        else:
            st.error(f"Player {remove_player_name} not found!")

# Change score of player and number of games played
st.header("Change score and number of games for player:")
player_name = st.selectbox("Select player", players.get_names())
if player_name:
    player = players.get_player_by_name(player_name)
    new_score = st.number_input("New score", value=player.score)
    new_games_played = st.number_input("New games played", value=player.games_played)  # noqa E501
    if st.button("Change Score"):
        player.score = new_score
        player.games_played = new_games_played
        update_player_session_state(players)
        st.success(f"Score of {player_name} changed to {new_score}!")
        st.rerun()
