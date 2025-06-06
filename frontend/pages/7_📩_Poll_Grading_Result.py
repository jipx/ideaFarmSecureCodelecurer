import streamlit as st
import requests

# Configure the Streamlit page
st.set_page_config(page_title="📩 Poll Grading Result", layout="wide")
st.title("📩 Check Grading Result")

# --- API Endpoint for polling ---
POLL_API_ENDPOINT = st.secrets.get("POLL_API", "https://your-api-url/poll")

st.info("Enter your submission ID to retrieve the latest grading result and report link.")

# --- Input field for submission ID ---
submission_id = st.text_input("Submission ID")

# --- Poll grading status ---
if submission_id and st.button("🔍 Check Status"):
    try:
        # Make GET request to polling API
        response = requests.get(POLL_API_ENDPOINT, params={"submission_id": submission_id})
        response.raise_for_status()

        # Parse response
        result = response.json()

        st.subheader("📊 Grading Summary")
        st.write(f"**Status:** {'✅ Completed' if result['status'] == 'complete' else '⏳ In Progress'}")
        st.write(f"**Score:** {result.get('score', 'N/A')}")

        # Link to report if available
        if result.get("report_url"):
            st.markdown(f"[📄 Download Report]({result['report_url']})", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Failed to retrieve grading status: {e}")