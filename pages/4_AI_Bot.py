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

# ── Load data for context ──
df = load_data()

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

data_context = f"""
You are an expert IPL cricket analyst. You have access to IPL data from 2008 to 2025.
Here is a summary of the data:
- Total Matches: {total_matches}
- Total Seasons: {total_seasons}
- Total Players: {total_players}
- Total Runs Scored: {total_runs}
- All Time Top Scorer: {top_scorer} with {top_scorer_runs} runs
- All Time Top Wicket Taker: {top_bowler} with {top_bowler_wickets} wickets
- Teams in dataset: {', '.join(teams)}

Answer questions about IPL stats, players, teams, records, and history.
Be conversational, fun and use cricket emojis. Keep answers concise but informative.
If asked something outside IPL cricket, politely redirect back to IPL.
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