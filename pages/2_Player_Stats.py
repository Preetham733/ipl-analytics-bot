import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data_loader import load_data
from utils.analysis import get_all_players

st.set_page_config(page_title="Player Stats", page_icon="🏏", layout="wide")
st.title("🏏 Player Stats")

df = load_data()

# ── Player selector ──
players = get_all_players(df)
selected_player = st.selectbox("Search a Player", players)

st.markdown("---")

# ── Figure out role ──
player_batting = df[df["batter"] == selected_player]
player_bowling = df[df["bowler"] == selected_player]

total_runs = player_batting["runs_batter"].sum()
total_balls_bowled = len(player_bowling)
wickets_df = player_bowling[
    player_bowling["wicket_kind"].notna() & 
    (player_bowling["wicket_kind"] != "run out")
]
total_wickets = len(wickets_df)

# Decide role
if total_runs > 200 and total_wickets > 20:
    role = "⚡ All Rounder"
elif total_wickets > total_runs / 20:
    role = "🎯 Bowler"
else:
    role = "🏏 Batter"

st.subheader(f"{selected_player} — {role}")

st.markdown("---")

# ── Batting stats ──
st.subheader("🏏 Batting Stats")

matches_batted = player_batting["match_id"].nunique()
fours = player_batting[player_batting["runs_batter"] == 4].shape[0]
sixes = player_batting[player_batting["runs_batter"] == 6].shape[0]
avg = round(total_runs / matches_batted, 2) if matches_batted > 0 else 0
balls_faced = len(player_batting)
strike_rate = round((total_runs / balls_faced) * 100, 2) if balls_faced > 0 else 0

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Total Runs", total_runs)
col2.metric("Matches", matches_batted)
col3.metric("Average", avg)
col4.metric("Strike Rate", strike_rate)
col5.metric("Fours", fours)
col6.metric("Sixes", sixes)

# Season wise runs chart
season_runs = player_batting.groupby("season")["runs_batter"].sum().reset_index()
season_runs.columns = ["season", "runs"]
if not season_runs.empty:
    fig1 = px.line(
        season_runs,
        x="season",
        y="runs",
        markers=True,
        title=f"{selected_player} - Runs Per Season"
    )
    st.plotly_chart(fig1, use_container_width=True)

# Scoring breakdown pie
breakdown = {
    "Type": ["Ones", "Twos", "Threes", "Fours", "Sixes"],
    "Count": [
        player_batting[player_batting["runs_batter"] == 1].shape[0],
        player_batting[player_batting["runs_batter"] == 2].shape[0],
        player_batting[player_batting["runs_batter"] == 3].shape[0],
        fours,
        sixes,
    ]
}
breakdown_df = pd.DataFrame(breakdown)
fig2 = px.pie(
    breakdown_df,
    names="Type",
    values="Count",
    title=f"{selected_player} - Scoring Breakdown",
    color_discrete_sequence=px.colors.sequential.Oranges
)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ── Bowling stats ──
st.subheader("🎯 Bowling Stats")

if total_balls_bowled == 0:
    st.info("No bowling data found for this player.")
else:
    matches_bowled = player_bowling["match_id"].nunique()
    overs_bowled = round(total_balls_bowled / 6, 1)
    total_runs_given = player_bowling["runs_total"].sum()
    economy = round(total_runs_given / (total_balls_bowled / 6), 2) if total_balls_bowled > 0 else 0
    bowling_avg = round(total_runs_given / total_wickets, 2) if total_wickets > 0 else "N/A"

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Wickets", total_wickets)
    col2.metric("Matches Bowled", matches_bowled)
    col3.metric("Overs Bowled", overs_bowled)
    col4.metric("Economy", economy)
    col5.metric("Bowling Avg", bowling_avg)

    # Season wise wickets chart
    wickets_per_season = wickets_df.groupby("season").size().reset_index(name="wickets")
    if not wickets_per_season.empty:
        fig3 = px.bar(
            wickets_per_season,
            x="season",
            y="wickets",
            title=f"{selected_player} - Wickets Per Season",
            color="wickets",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig3, use_container_width=True)