import os
import streamlit as st
from americano.players import PlayerList
from dotenv import load_dotenv

load_dotenv()
os.getenv("SAVED_PLAYERS")

if os.getenv("SAVED_PLAYERS"):
    SAVED_PLAYERS = os.getenv("SAVED_PLAYERS").split(",", )
    SAVED_PLAYERS = [player.strip() for player in SAVED_PLAYERS]
else:
    SAVED_PLAYERS = []

st.title("Americano Volleyball app")

# Initialize or load the player list in session state
if "players" not in st.session_state:
    st.session_state["players"] = PlayerList().model_dump_json()
players = PlayerList.parse_raw(st.session_state["players"])

if "reset_confirmation" not in st.session_state:
    st.session_state["reset_confirmation"] = False

# Display saved players list in sidebar with a button to load them
if SAVED_PLAYERS:
    st.sidebar.write("Saved players:")
    for i, player_name in enumerate(SAVED_PLAYERS):
        if player_name not in players.get_names():  # noqa E501
            if st.sidebar.button(f"Load {player_name}"):
                players.add_player(player_name)
                st.session_state["players"] = players.model_dump_json()
                st.success(f"Player {player_name} loaded!")


# Add Player
new_player_name = st.text_input("Add a new player")
if st.button("Add Player"):
    players.add_player(new_player_name)
    st.session_state["players"] = players.model_dump_json()
    st.success(f"Player {new_player_name} added!")


st.sidebar.divider()
# Load all saved players
if st.sidebar.button("Load all saved players"):
    for player_name in SAVED_PLAYERS:
        if player_name not in players.get_names():
            players.add_player(player_name)
            st.success(f"Player {player_name} loaded!")
    st.session_state["players"] = players.model_dump_json()
st.sidebar.divider()

# Reset button in sidebar
if st.sidebar.button("Reset"):
    # Are you sure message popup
    st.session_state["reset_confirmation"] = True
if st.session_state["reset_confirmation"]:
    st.sidebar.write("Are you sure you want to reset? Press either Yes or No")
    if st.sidebar.button("Yes"):
        st.session_state["players"] = PlayerList().model_dump_json()
        st.success("Player list reset!")
        st.session_state["reset_confirmation"] = False
        st.rerun()
    if st.sidebar.button("No"):
        st.session_state["reset_confirmation"] = False
        st.rerun()


# Display players based on pandas dataframe
st.write("List of players:")
if players.players:
    st.dataframe(
        players.to_pandas(),
        width=1000,
        height=1000
    )
else:
    st.write("No players added yet")


if not players.players:
    st.stop()

# Remove player by name
remove_player_name = st.selectbox("Select player to remove", players.get_names())  # noqa E501

if st.button("Remove Player"):
    player = players.remove_player_by_name(remove_player_name)  # noqa E501
    if player:
        st.session_state["players"] = players.model_dump_json()
        st.success(f"Player {remove_player_name} removed!")
        st.rerun()
    else:
        st.error(f"Player {remove_player_name} not found!")


# Change score of player
st.write("Change score of player:")
player_name = st.selectbox("Select player", players.get_names())
player = players.get_player_by_name(player_name)
new_score = st.number_input("New score", value=player.score)
if st.button("Change Score"):
    player.score = new_score
    st.session_state["players"] = players.model_dump_json()
    st.success(f"Score of {player_name} changed to {new_score}!")
    st.rerun()
