import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    df = pd.read_csv("data/IPL.csv")
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df