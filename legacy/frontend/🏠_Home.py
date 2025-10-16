import streamlit as st

from frontend.panes.common import at_start

at_start()

st.title("Americano App for Volleyball🏐")

intro = """\
This app was created for a volleyball tournament with a format inspired by the \
padel game Mexicano 🏸 (a variant of Americano), but where more flexibility was needed \
with respect to number of players on each court and the number of courts in \
each round. The app allows for *a variable number of players on each court* and \
*a variable number of courts in each round*. \
"""  # noqa E501

mexicano_description = """\
The Mexicano padel tournament is a dynamic, social format where players are \
paired based on their current standings, ensuring evenly matched games as the \
tournament progresses. Players accumulate individual points from each match, \
and the player with the most points at the end wins. \
[You can read more about the Mexicano variant here]\
(https://pistas365.com/padel/information/rules/mexicano-tournament/). \
"""

st.markdown(intro)

st.subheader("The Mexicano Padel Tournament format")
st.markdown(mexicano_description)

st.markdown("\n\nHope you enjoy the app!")


# House emoji 🏠