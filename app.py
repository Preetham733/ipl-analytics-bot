import streamlit as st
from utils.data_loader import load_data

st.set_page_config(
    page_title="IPL Analytics Bot",
    page_icon="🏏",
    layout="wide"
)

st.title("🏏 IPL Analytics Bot")
st.subheader("2008 – 2025 | Built by Preetham")

st.markdown("---")

df = load_data()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Matches", df["match_id"].nunique())

with col2:
    st.metric("Total Seasons", df["season"].nunique())

with col3:
    st.metric("Total Players", df["batter"].nunique())

with col4:
    st.metric("Total Runs Scored", f"{df['runs_batter'].sum():,}")

st.markdown("---")

st.markdown("""
### 📌 Navigate using the sidebar:
- **Team Stats** — Season-wise wins, top teams
- **Player Stats** — Top batters, bowlers, individual profiles
- **Head to Head** — Team vs Team records
- **AI Bot** — Ask anything about IPL 🤖
""")

st.success("✅ Data loaded! Use the sidebar to explore.")