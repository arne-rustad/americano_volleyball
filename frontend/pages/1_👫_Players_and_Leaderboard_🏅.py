import os

import streamlit as st
from dotenv import load_dotenv

from americano.players import PlayerList

load_dotenv()

st.set_page_config(layout="wide")


def update_player_session_state(players):
    st.session_state["players"] = players.model_dump_json()


if os.getenv("SAVED_PLAYERS"):
    SAVED_PLAYERS = os.getenv("SAVED_PLAYERS").split(",", )
    SAVED_PLAYERS = [player.strip() for player in SAVED_PLAYERS]
else:
    SAVED_PLAYERS = []

st.title("Player management and leaderboard")
main, sidebar = st.columns([2, 1])

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
    for player_name in SAVED_PLAYERS:
        if player_name in players.get_names():
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

with sidebar:
    # Add Player
    st.header("")
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

with main:
    # Display players based on pandas dataframe
    st.header("Players:")
    df_players = players.to_pandas()
    df_players.rename(
        columns={"id": "ID", "name": "Name", "score": "Score", "games_played": "Games Played"},  # noqa E501
        inplace=True
    )
    if players.players:
        st.dataframe(
            df_players,
            width=1000,
            height=int(35.2*(len(players.players)+1))
        )
    else:
        st.write("No players added yet")
        st.stop()

with sidebar:
    if "game_session" in st.session_state:
        st.write("Game session is active. End the session to remove players.")
    else:
        # Remove player by name
        remove_player_name = st.selectbox("Select player to remove", players.get_names())  # noqa E501

        if st.button("Remove Player"):
            player = players.remove_player_by_name(remove_player_name)
            if player:
                update_player_session_state(players)
                st.success(f"Player {remove_player_name} removed!")
                st.rerun()
            else:
                st.error(f"Player {remove_player_name} not found!")

with sidebar:
    # Change score of player and number of games played
    st.subheader("Change score and number of games for player:")
    st.write("Should only be used to make manual corrections for edge cases.")
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
