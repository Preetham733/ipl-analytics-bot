import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    file_id = "1jeS0eD-g2QQIROaUApSm_NXXvbO4WQSv"
    url = f"https://drive.google.com/uc?id={file_id}"
    df = pd.read_csv(url)
    
    # Show actual column names for debugging
    st.write("Columns found:", df.columns.tolist())
    
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df