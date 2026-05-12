import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    file_id = "1jeS0eD-g2QQIROaUApSm_NXXvbO4WQSv"
    url = f"https://drive.usercontent.google.com/download?id={file_id}&confirm=t"
    df = pd.read_csv(url, low_memory=False, index_col=0)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df