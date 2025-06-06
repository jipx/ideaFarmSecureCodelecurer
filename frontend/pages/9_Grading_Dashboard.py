import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="📊 Grading Dashboard", layout="wide")
st.title("📊 Grading Dashboard")

DASHBOARD_API_URL = st.secrets["apigateway"]["DASHBOARD_API_URL"]




with st.spinner("Loading submissions..."):
    try:
        res = requests.get(DASHBOARD_API_URL)
        if res.status_code == 200:
            data = res.json()
        else:
            st.error(f"Error fetching data: {res.status_code}")
            st.stop()
    except Exception as e:
        st.error(f"Request failed: {e}")
        st.stop()

if data:
    df = pd.DataFrame(data)
    if "report_url" in df.columns:
        df["Download Report"] = df["report_url"].apply(lambda url: f"[Download]({url})")
    st.markdown("### Submissions Summary")
    st.dataframe(df[["submission_id", "status", "score", "Download Report"] if "Download Report" in df.columns else ["submission_id", "status", "score"]], use_container_width=True)
else:
    st.info("No submissions found.")
