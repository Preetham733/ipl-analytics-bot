import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv
from utils.data_loader import load_data

load_dotenv()

st.set_page_config(page_title="IPL AI Bot", page_icon="🤖", layout="wide")
st.title("🤖 IPL AI Bot")
st.subheader("Ask me anything about IPL!")

# ── Load API key ──
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("❌ Groq API key not found! Add it to your .env file.")
    st.stop()

client = Groq(api_key=api_key)

# ── Load data ──
df = load_data()

# ── Build context ──
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

# Team all time wins
team_wins = df.drop_duplicates(subset=["match_id"])["match_won_by"].value_counts().reset_index()
team_wins.columns = ["team", "wins"]
team_wins_str = "\n".join([f"  - {row['team']}: {row['wins']} wins" for _, row in team_wins.iterrows()])

# Team runs per season
team_season_runs = df.groupby(["season", "batting_team"])["runs_batter"].sum().reset_index()
team_season_runs_str = "\n".join([
    f"  - {row['batting_team']} in {row['season']}: {row['runs_batter']} runs"
    for _, row in team_season_runs.iterrows()
])

# Season winners
match_df = df.drop_duplicates(subset=["match_id"])
season_winners = match_df.groupby("season")["match_won_by"].agg(
    lambda x: x.value_counts().index[0]
).reset_index()
season_winners_str = "\n".join([
    f"  - {row['season']}: {row['match_won_by']}"
    for _, row in season_winners.iterrows()
])

data_context = f"""
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

TEAM RUNS PER SEASON (use this for exact answers):
{team_season_runs_str}

MOST WINS PER SEASON:
{season_winners_str}

INSTRUCTIONS:
- You have EXACT data above. Always use it to give precise answers.
- When asked about a team runs in a season, look up TEAM RUNS PER SEASON and give the exact number.
- Never say you dont have data if it is listed above.
- Understand informal or badly typed English. "srh runs 2023" means "SunRisers Hyderabad runs in 2023".
- Be conversational and fun, use cricket emojis.
- For predictions, give fun analysis based on historical data.
- Keep answers concise but informative.
"""

# ── Chat history ──
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Display chat history ──
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Suggested questions ──
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

# ── Chat input ──
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
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": data_context},
                    *[{"role": m["role"], "content": m["content"]}
                      for m in st.session_state.messages]
                ]
            )
            answer = response.choices[0].message.content
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})