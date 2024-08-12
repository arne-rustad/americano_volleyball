import streamlit as st

st.header("Americano App for Volleyball🏐")

intro = """\
This app was created for a volleyball tournament inspired by the padel game \
Mexicano 🏸 (a variant of Americano), but where more flexibility was needed \
with respect to number of players on each court and the number of courts in \
each round. The app allows for a variable number of players on each court and \
a variable number of courts in each round.

[You can read more about the Mexicano variant here]\
(https://pistas365.com/padel/information/rules/mexicano-tournament/). \
The Mexicano padel tournament is a dynamic, social format where players are \
paired based on their current standings, ensuring evenly matched games as the \
tournament progresses. Players accumulate individual points from each match, \
and the player with the most points at the end wins.
"""

st.markdown(intro)
