import streamlit as st
import plotly.express as px
from utils.data_loader import load_data
from utils.analysis import get_all_teams, top_run_scorers, top_wicket_takers

st.set_page_config(page_title="Team Stats", page_icon="🏆", layout="wide")
st.title("🏆 Team Stats")

df = load_data()

# ── Season-wise wins chart ──
st.subheader("Season-wise Team Wins")

match_results = df.drop_duplicates(subset=["match_id"])[["season", "match_won_by"]]
wins = match_results.groupby(["season", "match_won_by"]).size().reset_index(name="wins")

teams = get_all_teams(df)
selected_teams = st.multiselect("Filter by Team", teams, default=teams[:4])

filtered = wins[wins["match_won_by"].isin(selected_teams)]

fig1 = px.bar(
    filtered,
    x="season",
    y="wins",
    color="match_won_by",
    barmode="group",
    title="Wins Per Season by Team"
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# ── Top Run Scorers ──
st.subheader("🏏 Top 10 Run Scorers (All Time)")
top_runs = top_run_scorers(df)
fig2 = px.bar(
    top_runs,
    x="total_runs",
    y="player",
    orientation="h",
    color="total_runs",
    color_continuous_scale="Oranges",
    title="Top 10 Batters by Total Runs"
)
fig2.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ── Top Wicket Takers ──
st.subheader("🎯 Top 10 Wicket Takers (All Time)")
top_wickets = top_wicket_takers(df)
fig3 = px.bar(
    top_wickets,
    x="wickets",
    y="bowler",
    orientation="h",
    color="wickets",
    color_continuous_scale="Blues",
    title="Top 10 Bowlers by Wickets"
)
fig3.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig3, use_container_width=True)