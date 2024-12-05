
import streamlit as st
import yaml

from americano.models.enums import Gender
from americano.paths import SAVED_PLAYERS_PATH
from frontend.config import INFO_ICON
from frontend.panes.common import at_start
from frontend.state.get_state import get_state

at_start()

state = get_state(user_id=st.session_state.session_id)

st.set_page_config(layout="wide")

tournament_options = state.get_tournament_options()
if tournament_options is None:
    st.info("You must first start a tournament.", icon=INFO_ICON)
    st.stop()

if SAVED_PLAYERS_PATH.exists():
    with open(SAVED_PLAYERS_PATH) as f:
        SAVED_PLAYERS = yaml.safe_load(f)
else:
    SAVED_PLAYERS = []

st.title("Player management and leaderboard")
sidebar, main = st.columns([1, 2])

players = state.get_players()

# Display saved players list in sidebar with a button to load them
if SAVED_PLAYERS:
    st.sidebar.header("Favorite players:")
    # Load all saved players
    player_names = players.get_names()
    favorites_not_loaded = []
    for player in SAVED_PLAYERS:
        if player["name"] not in player_names:
            favorites_not_loaded.append(player)
    
    if len(favorites_not_loaded) > 0:
        if len(favorites_not_loaded) > 1:
            if st.sidebar.button("Load all favorite players"):
                for player in favorites_not_loaded:
                    players.add_player(
                        name=player["name"],
                        gender=Gender(player["gender"])
                    )
                state.set_players(players)
                st.rerun()
            st.sidebar.divider()

        for player in favorites_not_loaded:
            if st.sidebar.button(f"Load {player['name']}"):
                players.add_player(name=player["name"], gender=Gender(player["gender"]))  # noqa E501
                state.set_players(players)
                st.success(f"Player {player['name']} loaded!")
                st.rerun()
        st.sidebar.divider()
    else:
        st.sidebar.info("All favorite players already loaded!", icon=INFO_ICON)
        st.sidebar.divider()

with sidebar:
    # Add Player
    st.header("Add player")
    with st.form(key="add_player", clear_on_submit=True):
        new_player_name = st.text_input("Player name")
        new_player_gender = st.radio(
            label="Select player",
            options=["Male", "Female"],
        )
        btn_add_player = st.form_submit_button("Add player")
        if btn_add_player:
            try:
                players.add_player(
                    name=new_player_name,
                    gender=new_player_gender.lower(),
                )
                state.set_players(players)
                st.success(f"Player {new_player_name} added!")
            except ValueError as e:
                st.error(e)


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
            "gender": "Gender",
        },
        inplace=True,
    )
    if players.players:
        if tournament_options.mix_tournament:
                df_players["Gender"] = df_players["Gender"].apply(lambda x: x.capitalize())  # noqa E501
        else:
            df_players.drop(columns=["Gender"], inplace=True)

        st.dataframe(
            df_players,
            width=1000,
            height=int(35.2 * (len(players.players) + 1)),
            hide_index=True,
        )
    else:
        st.info("No players added yet", icon=INFO_ICON)
        st.stop()

with sidebar:
    st.header("Remove player")
    if "game_session" in st.session_state:
        st.write("Game session is active. End the session to remove players.")
    else:
        confirm_before_removing_player = st.checkbox("Confirm before removing player", value=True)  # noqa E501
        # Remove player by name
        remove_player_name = st.selectbox(
            "Select player to remove", players.get_names()
        )

        if st.button("Remove Player"):
            @st.dialog("Are you sure you want to remove this player?")
            def remove_player_dialog():
                if st.button("Yes, remove player."):
                    player = players.remove_player_by_name(remove_player_name)
                    if player:
                        state.set_players(players)
                        st.success(f"Player {remove_player_name} removed!")
                        st.rerun()
                    else:
                        st.error(f"Player {remove_player_name} not found!")
            if confirm_before_removing_player:
                remove_player_dialog()
            else:
                player = players.remove_player_by_name(remove_player_name)
                if player:
                    state.set_players(players)
                    st.success(f"Player {remove_player_name} removed!")
                    st.rerun()
                else:
                    st.error(f"Player {remove_player_name} not found!")

    st.header("Other actions")
    # Change score of player and number of games played
    with st.expander("Make manual adjustments"):
        st.info(
        "Should only be used to make manual corrections for edge cases.",
            icon=INFO_ICON,
        )
        player_name = st.selectbox("Select player", players.get_names())
        if player_name:
            player = players.get_player_by_name(player_name)

            st.write(f"**Adjust player details for {player_name}**")
            with st.form(key="change_player_details"):
                new_score = st.number_input("New score", value=player.score)
                new_games_played = st.number_input(
                    "New games played", value=player.games_played
                )
                new_gender = st.radio(
                    label="New gender",
                    options=["Male", "Female"],
                    index=0 if player.gender == Gender.MALE.value else 1,
                )
                new_name = st.text_input("New name", value=player.name)
                if st.form_submit_button("Update Player Details"):
                    old_score = player.score
                    old_games_played = player.games_played
                    old_gender = player.gender
                    old_name = player_name
                    players.edit_player(
                        player_id=player.id,
                        new_score=new_score,
                        new_games_played=new_games_played,
                        new_gender=new_gender.lower(),
                        new_name=new_name,
                    )
                    state.set_players(players)
                    st.success(f"Player details updated for **{player_name}**")
                    if new_score != old_score:  
                        st.success(f"Score changed to **{new_score}** from {old_score}")  # noqa E501
                    if new_games_played != old_games_played:
                        st.success(f"Games played changed to **{new_games_played}** from {old_games_played}")  # noqa E501
                    if new_gender.lower() != old_gender.lower():
                        st.success(f"Gender changed to **{new_gender}** from {old_gender.capitalize()}")  # noqa E501
                    if new_name != old_name:
                        st.success(f"Name changed to **{new_name}** from {old_name}")  # noqa E501


    @st.dialog("Are you sure you want to restart the tournament?")
    def restart_tournament_dialog():
        st.write("**This will reset all scores and games played to zero. There will be no way to undo this.**")  # noqa E501
        if st.button("Yes, restart tournament."):
            state.restart_tournament()
            st.success("Tournament restarted.")
            st.rerun()

    if st.button("Restart Tournament"):
        restart_tournament_dialog()
