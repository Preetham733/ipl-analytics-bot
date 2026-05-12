import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data_loader import load_data
from utils.analysis import get_all_teams, head_to_head

st.set_page_config(page_title="Head to Head", page_icon="⚔️", layout="wide")
st.title("⚔️ Head to Head")

df = load_data()
teams = get_all_teams(df)

col1, col2 = st.columns(2)
with col1:
    team1 = st.selectbox("Select Team 1", teams, index=0)
with col2:
    team2 = st.selectbox("Select Team 2", teams, index=1)

if team1 == team2:
    st.warning("Please select two different teams!")
else:
    st.markdown("---")

    # ── Filter H2H matches ──
    h2h_df = df[
        ((df["batting_team"] == team1) | (df["batting_team"] == team2)) &
        ((df["bowling_team"] == team1) | (df["bowling_team"] == team2))
    ]

    results = head_to_head(df, team1, team2)

    # ── Win count cards ──
    st.subheader(f"🏆 {team1} vs {team2} — All Time Record")

    col1, col2, col3 = st.columns(3)
    team1_wins = results[results["team"] == team1]["wins"].values
    team2_wins = results[results["team"] == team2]["wins"].values
    team1_wins = int(team1_wins[0]) if len(team1_wins) > 0 else 0
    team2_wins = int(team2_wins[0]) if len(team2_wins) > 0 else 0
    total_matches = team1_wins + team2_wins

    col1.metric(f"{team1} Wins", team1_wins)
    col2.metric("Total Matches", total_matches)
    col3.metric(f"{team2} Wins", team2_wins)

    st.markdown("---")

    # ── Pie chart ──
    st.subheader("Win Share")
    fig1 = px.pie(
        results,
        names="team",
        values="wins",
        title=f"{team1} vs {team2} - Win %",
        color_discrete_sequence=["#FF6B35", "#004E89"]
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")

    # ── Season wise H2H ──
    st.subheader("📅 Season by Season Results")
    season_results = h2h_df.drop_duplicates(subset=["match_id"])[["season", "match_won_by"]]
    season_results = season_results[season_results["match_won_by"].isin([team1, team2])]
    season_wins = season_results.groupby(["season", "match_won_by"]).size().reset_index(name="wins")

    fig2 = px.bar(
        season_wins,
        x="season",
        y="wins",
        color="match_won_by",
        barmode="group",
        title=f"{team1} vs {team2} - Season Wise Wins",
        color_discrete_map={team1: "#FF6B35", team2: "#004E89"}
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── Top Run Scorers & Wicket Takers side by side ──
    col_bat, col_bowl = st.columns(2)

    with col_bat:
        st.subheader("🏏 Top Run Scorers")
        top_batters = h2h_df.groupby("batter")["runs_batter"].sum().reset_index()
        top_batters.columns = ["player", "runs"]
        top_batters = top_batters.sort_values("runs", ascending=False).head(10)
        fig3 = px.bar(
            top_batters,
            x="runs",
            y="player",
            orientation="h",
            color="runs",
            color_continuous_scale="Oranges",
            title="Top 10 Batters"
        )
        fig3.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig3, use_container_width=True)

    with col_bowl:
        st.subheader("🎯 Top Wicket Takers")
        wickets_h2h = h2h_df[
            h2h_df["wicket_kind"].notna() &
            (h2h_df["wicket_kind"] != "run out")
        ]
        top_bowlers = wickets_h2h.groupby("bowler").size().reset_index(name="wickets")
        top_bowlers = top_bowlers.sort_values("wickets", ascending=False).head(10)
        fig4 = px.bar(
            top_bowlers,
            x="wickets",
            y="bowler",
            orientation="h",
            color="wickets",
            color_continuous_scale="Blues",
            title="Top 10 Bowlers"
        )
        fig4.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")

    # ── Detailed Match Scorecards ──
    st.subheader("📋 Match by Match Scorecards")

    all_matches = h2h_df.drop_duplicates(subset=["match_id"])[["match_id", "season", "date", "match_won_by"]].sort_values("date", ascending=False)

    for _, match_row in all_matches.iterrows():
        mid = match_row["match_id"]
        winner = match_row["match_won_by"]
        season = match_row["season"]
        date = match_row["date"]

        with st.expander(f"📅 {date} | Season {season} | 🏆 Winner: {winner}"):

            match_df = h2h_df[h2h_df["match_id"] == mid]

            # ── Batting scorecard per innings ──
            for innings_num in sorted(match_df["innings"].unique()):
                innings_df = match_df[match_df["innings"] == innings_num]
                batting_team = innings_df["batting_team"].iloc[0]

                st.markdown(f"**🏏 Innings {innings_num} — {batting_team} Batting**")

                # Batter stats
                batter_stats = innings_df.groupby("batter").agg(
                    runs=("runs_batter", "sum"),
                    balls=("runs_batter", "count"),
                    fours=("runs_batter", lambda x: (x == 4).sum()),
                    sixes=("runs_batter", lambda x: (x == 6).sum()),
                ).reset_index()
                batter_stats["SR"] = (batter_stats["runs"] / batter_stats["balls"] * 100).round(1)

                # Who got out and by whom
                dismissals = innings_df[innings_df["player_out"].notna()][["player_out", "bowler", "wicket_kind"]]
                dismissals.columns = ["batter", "bowler", "how_out"]

                batter_stats = batter_stats.merge(dismissals, on="batter", how="left")
                batter_stats["how_out"] = batter_stats["how_out"].fillna("not out")
                batter_stats["bowler"] = batter_stats["bowler"].fillna("-")

                batter_stats = batter_stats.rename(columns={
                    "batter": "Batter",
                    "runs": "Runs",
                    "balls": "Balls",
                    "fours": "4s",
                    "sixes": "6s",
                    "how_out": "Dismissal",
                    "bowler": "Bowler"
                })

                total_runs = innings_df["runs_total"].sum()
                total_wickets = innings_df["wicket_kind"].notna().sum()
                st.markdown(f"**Total: {total_runs}/{total_wickets}**")
                st.dataframe(batter_stats[["Batter", "Runs", "Balls", "SR", "4s", "6s", "Dismissal", "Bowler"]], use_container_width=True)

                # Bowler stats
                st.markdown(f"**🎯 Bowling Figures**")
                bowler_stats = innings_df.groupby("bowler").agg(
                    overs=("ball", lambda x: round(len(x) / 6, 1)),
                    runs=("runs_total", "sum"),
                    wickets=("wicket_kind", lambda x: x[x.notna() & (x != "run out")].count())
                ).reset_index()
                bowler_stats["economy"] = (bowler_stats["runs"] / bowler_stats["overs"]).round(2)
                bowler_stats = bowler_stats.rename(columns={
                    "bowler": "Bowler",
                    "overs": "Overs",
                    "runs": "Runs",
                    "wickets": "Wickets",
                    "economy": "Economy"
                })
                st.dataframe(bowler_stats[["Bowler", "Overs", "Runs", "Wickets", "Economy"]], use_container_width=True)

                st.markdown("---")