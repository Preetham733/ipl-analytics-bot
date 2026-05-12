import streamlit as st
from groq import Groq
import os
import pandas as pd
from dotenv import load_dotenv
from utils.data_loader import load_data

load_dotenv()

st.set_page_config(page_title="IPL AI Bot", page_icon="🤖", layout="wide")
st.title("🤖 IPL AI Bot")
st.subheader("Ask me anything about IPL!")

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("❌ Groq API key not found!")
    st.stop()

client = Groq(api_key=api_key)
df = load_data()

# ── Base context ──
total_matches = df["match_id"].nunique()
total_seasons = df["season"].nunique()
total_players = df["batter"].nunique()
total_runs = df["runs_batter"].sum()

top_scorer = df.groupby("batter")["runs_batter"].sum().idxmax()
top_scorer_runs = df.groupby("batter")["runs_batter"].sum().max()

wickets_df = df[df["wicket_kind"].notna() & (df["wicket_kind"] != "run out")]
top_bowler = wickets_df.groupby("bowler").size().idxmax()
top_bowler_wickets = wickets_df.groupby("bowler").size().max()

teams = df["batting_team"].dropna().unique().tolist()
all_players = df["batter"].dropna().unique().tolist()

team_wins = df.drop_duplicates(subset=["match_id"])["match_won_by"].value_counts().reset_index()
team_wins.columns = ["team", "wins"]
team_wins_str = "\n".join([f"  - {row['team']}: {row['wins']} wins" for _, row in team_wins.iterrows()])

team_season_runs = df.groupby(["season", "batting_team"])["runs_batter"].sum().reset_index()
team_season_runs_str = "\n".join([
    f"  - {row['batting_team']} in {row['season']}: {row['runs_batter']} runs"
    for _, row in team_season_runs.iterrows()
])

match_df = df.drop_duplicates(subset=["match_id"])
season_winners = match_df.groupby("season")["match_won_by"].agg(
    lambda x: x.value_counts().index[0]
).reset_index()
season_winners_str = "\n".join([
    f"  - {row['season']}: {row['match_won_by']}"
    for _, row in season_winners.iterrows()
])

# ── Smart player finder ──
from thefuzz import process

def find_player_in_query(query, all_players):
    # First try exact match
    query_lower = query.lower()
    for player in all_players:
        if player.lower() in query_lower:
            return player

    # Try partial match word by word
    for player in all_players:
        parts = player.lower().split()
        for part in parts:
            if len(part) > 3 and part in query_lower:
                return player

    # Try fuzzy match on each word in quer
    words = query_lower.split()
    for word in words:
        if len(word) > 4:
            match, score = process.extractOne(word, [p.lower() for p in all_players])
            if score > 75:
                # Return original case player name
                idx = [p.lower() for p in all_players].index(match)
                return all_players[idx]

    return None

def get_player_context(player_name):
    # Batting stats
    bat_df = df[df["batter"] == player_name]
    total_runs = bat_df["runs_batter"].sum()
    matches = bat_df["match_id"].nunique()
    fours = (bat_df["runs_batter"] == 4).sum()
    sixes = (bat_df["runs_batter"] == 6).sum()
    balls = len(bat_df)
    sr = round((total_runs / balls * 100), 2) if balls > 0 else 0
    avg = round(total_runs / matches, 2) if matches > 0 else 0

    # Season wise batting
    season_bat = bat_df.groupby("season")["runs_batter"].sum().reset_index()
    season_bat_str = "\n".join([f"    {row['season']}: {row['runs_batter']} runs" for _, row in season_bat.iterrows()])

    # Bowling stats
    bowl_df = df[df["bowler"] == player_name]
    w_df = bowl_df[bowl_df["wicket_kind"].notna() & (bowl_df["wicket_kind"] != "run out")]
    total_wickets = len(w_df)
    balls_bowled = len(bowl_df)
    runs_given = bowl_df["runs_total"].sum()
    economy = round(runs_given / (balls_bowled / 6), 2) if balls_bowled > 0 else 0
    bowling_avg = round(runs_given / total_wickets, 2) if total_wickets > 0 else "N/A"

    # Season wise bowling
    season_bowl = w_df.groupby("season").size().reset_index(name="wickets")
    season_bowl_str = "\n".join([f"    {row['season']}: {row['wickets']} wickets" for _, row in season_bowl.iterrows()])

    return f"""
PLAYER STATS FOR {player_name}:
BATTING:
- Total Runs: {total_runs}
- Matches: {matches}
- Average: {avg}
- Strike Rate: {sr}
- Fours: {fours}
- Sixes: {sixes}
Season wise runs:
{season_bat_str}

BOWLING:
- Total Wickets: {total_wickets}
- Economy: {economy}
- Bowling Average: {bowling_avg}
Season wise wickets:
{season_bowl_str}
"""

base_context = f"""
You are an expert IPL cricket analyst with access to ball by ball IPL data from 2008 to 2025.

DATASET SUMMARY:
- Total Matches: {total_matches}
- Total Seasons: {total_seasons}
- Total Players: {total_players}
- Total Runs Scored: {total_runs}
- All Time Top Scorer: {top_scorer} with {top_scorer_runs} runs
- All Time Top Wicket Taker: {top_bowler} with {top_bowler_wickets} wickets
- Teams: {', '.join(teams)}

TEAM ALL TIME WIN COUNT:
{team_wins_str}

TEAM RUNS PER SEASON:
{team_season_runs_str}

MOST WINS PER SEASON:
{season_winners_str}

INSTRUCTIONS:
- You have EXACT data. Always use it for precise answers.
- Never say you dont have data if it is listed above.
- Understand informal or badly typed English.
- Be conversational and fun, use cricket emojis.
- For predictions, give fun analysis based on historical data.
- Keep answers concise but informative.
"""

# ── Chat history ──
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if len(st.session_state.messages) == 0:
    st.markdown("### 💡 Try asking:")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🏏 Who has scored the most runs?"):
            st.session_state.starter = "Who has scored the most runs in IPL history?"
    with col2:
        if st.button("🎯 Best bowler in IPL?"):
            st.session_state.starter = "Who is the best bowler in IPL history?"
    with col3:
        if st.button("🏆 Most successful team?"):
            st.session_state.starter = "Which team has won the most IPL titles?"

prompt = st.chat_input("Ask anything about IPL...")

if "starter" in st.session_state:
    prompt = st.session_state.starter
    del st.session_state.starter

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            # Check if a player is mentioned
            player_found = find_player_in_query(prompt, all_players)
            if player_found:
                player_context = get_player_context(player_found)
                full_context = base_context + "\n" + player_context
            else:
                full_context = base_context

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": full_context},
                    *[{"role": m["role"], "content": m["content"]}
                      for m in st.session_state.messages]
                ]
            )
            answer = response.choices[0].message.content
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})