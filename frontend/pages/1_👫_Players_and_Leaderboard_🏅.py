import os

import streamlit as st
from dotenv import load_dotenv

from frontend.config import INFO_ICON
from frontend.utils.state import get_players_from_state, update_players_state

load_dotenv()

st.set_page_config(layout="wide")


if os.getenv("SAVED_PLAYERS"):
    SAVED_PLAYERS = os.getenv("SAVED_PLAYERS").split(
        ",",
    )
    SAVED_PLAYERS = [player.strip() for player in SAVED_PLAYERS]
else:
    SAVED_PLAYERS = []

st.title("Player management and leaderboard")
main, sidebar = st.columns([2, 1])

players = get_players_from_state()

if (
    st.session_state.get("reset_confirmation") is None
    or st.session_state.get("reset_confirmation") is False
):
    reset_confirmation = False
else:
    reset_confirmation = True
    st.session_state["reset_confirmation"] = False

# Display saved players list in sidebar with a button to load them
if SAVED_PLAYERS:
    st.sidebar.header("Favorite players:")
    # Load all saved players
    player_names = players.get_names()
    favorites_not_loaded = []
    for player_name in SAVED_PLAYERS:
        if player_name not in player_names:
            favorites_not_loaded.append(player_name)
    
    if len(favorites_not_loaded) > 0:
        if len(favorites_not_loaded) > 1:
            if st.sidebar.button("Load all favorite players"):
                for player_name in SAVED_PLAYERS:
                    if player_name not in player_names:
                        players.add_player(player_name)
                update_players_state(players)
                st.rerun()
            st.sidebar.divider()
    
        for player_name in favorites_not_loaded:
            if st.sidebar.button(f"Load {player_name}"):
                players.add_player(player_name)
                update_players_state(players)
                st.success(f"Player {player_name} loaded!")
                st.rerun()
        st.sidebar.divider()
    else:
        st.sidebar.info("All favorite players already loaded!", icon=INFO_ICON)
        st.sidebar.divider()

with sidebar:
    # Add Player
    st.header("")
    new_player_name = st.text_input("Add a new player")
    if st.button("Add Player"):
        try:
            players.add_player(new_player_name)
            update_players_state(players)
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

with main:
    # Display players based on pandas dataframe
    st.header("Players:")
    df_players = players.to_pandas()
    df_players.rename(
        columns={
            "id": "ID",
            "name": "Name",
            "score": "Score",
            "games_played": "Games Played",
        },
        inplace=True,
    )
    if players.players:
        st.dataframe(
            df_players,
            width=1000,
            height=int(35.2 * (len(players.players) + 1)),
        )
    else:
        st.info("No players added yet", icon=INFO_ICON)
        st.stop()

with sidebar:
    if "game_session" in st.session_state:
        st.write("Game session is active. End the session to remove players.")
    else:
        # Remove player by name
        remove_player_name = st.selectbox(
            "Select player to remove", players.get_names()
        )

        if st.button("Remove Player"):
            player = players.remove_player_by_name(remove_player_name)
            if player:
                update_players_state(players)
                st.success(f"Player {remove_player_name} removed!")
                st.rerun()
            else:
                st.error(f"Player {remove_player_name} not found!")

    # Change score of player and number of games played
    st.subheader("Change score and number of games for player:")
    st.info(
        "Should only be used to make manual corrections for edge cases.",
        icon=INFO_ICON,
    )
    player_name = st.selectbox("Select player", players.get_names())
    if player_name:
        player = players.get_player_by_name(player_name)
        new_score = st.number_input("New score", value=player.score)
        new_games_played = st.number_input(
            "New games played", value=player.games_played
        )
        if st.button("Change Score"):
            player.score = new_score
            player.games_played = new_games_played
            update_players_state(players)
            st.success(f"Score of {player_name} changed to {new_score}!")
            st.rerun()
