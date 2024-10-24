import streamlit as st

from frontend.config import INFO_ICON
from frontend.state.get_state import get_state

state = get_state(user_id="osvb_hostslepp")

st.title("🏅 Leaderboard")

# Get current tournament options from state
tournament_options = state.get_tournament_options()
player_list = state.get_players()

# Display players based on pandas dataframe
df_players = player_list.to_pandas()
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
if player_list.players:
    if tournament_options.mix_tournament:
        df_players["Gender"] = df_players["Gender"].apply(lambda x: x.capitalize())  # noqa E501
    else:
        df_players.drop(columns=["Gender"], inplace=True)
    
    df_players.sort_values(by="Score", ascending=False, inplace=True)

    st.write("**💡Hint:** Click on a column header to sort by that column. By default this is sorted by score.")  # noqa E501
    st.dataframe(
        df_players,
        width=1000,
        height=int(35.2 * (len(player_list.players) + 1)),
        hide_index=True,
    )

else:
    st.info("No players added yet", icon=INFO_ICON)
    st.stop()