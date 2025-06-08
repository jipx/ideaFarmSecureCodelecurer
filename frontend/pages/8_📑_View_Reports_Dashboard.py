import streamlit as st
import requests
import json
import streamlit.components.v1 as components
from urllib.parse import quote

st.set_page_config(page_title="Secure Code Grading Reports", layout="wide")
st.title("📑 View Secure Code Grading Reports")

API_URL = "https://u8w3qqosk4.execute-api.ap-northeast-1.amazonaws.com/prod/AllSubmissions"
REPORT_BUCKET_URL = "https://secure-code-reports.s3.amazonaws.com"

# === Utility: View Report Button with Modal-Style Overlay ===
def view_report_button(label: str, report_url: str, submission_id: str, key_suffix: str):
    """
    Renders a View Report button and loads the report into a modal-style expander with spinner.
    """
    if st.button(label, key=f"view_btn_{key_suffix}"):
        with st.spinner("🔄 Loading report..."):
            try:
                response = requests.get(report_url)
                response.raise_for_status()
                text = response.text

                with st.expander(f"📄 Report Preview: {submission_id}", expanded=True):
                    try:
                        parsed = json.loads(text)
                        preview = parsed.get("content") if isinstance(parsed, dict) else None

                        if preview and isinstance(preview, str):
                            st.markdown("#### 🖼️ Markdown Preview")
                            st.markdown(preview, unsafe_allow_html=True)
                        else:
                            st.markdown("#### 📦 Raw JSON Report")
                            st.json(parsed)
                    except json.JSONDecodeError:
                        if "<html" in text.lower():
                            st.markdown("#### 🖼️ HTML Preview")
                            components.html(text, height=400, scrolling=True)
                        else:
                            st.markdown("#### 📄 Plain Text Report")
                            st.code(text)
            except Exception as e:
                st.error(f"❌ Failed to load report: {e}")

# === Session State Setup ===
if "report_data" not in st.session_state:
    st.session_state.report_data = []

# === Fetch Reports ===
if st.button("🔍 Fetch All Reports"):
    with st.spinner("Calling API..."):
        try:
            response = requests.post(API_URL, headers={"Content-Type": "application/json"}, json={})
            response.raise_for_status()
            data = response.json()

            if isinstance(data, list) and data:
                st.session_state.report_data = data
                st.success(f"✅ Retrieved {len(data)} submissions.")

                with st.expander("📦 Show Raw JSON Response", expanded=False):
                    st.json(data)
            else:
                st.warning("⚠️ No data found or response was not a list.")
        except Exception as e:
            st.error(f"❌ Failed to fetch: {e}")

# === Display Submissions ===
for idx, row in enumerate(st.session_state.report_data):
    sid = row.get("submission_id", "❓ Unknown")
    email = row.get("email", "❓ Unknown")
    feedback = row.get("feedback_summary", "❌ Missing")
    report_key = row.get("report_key", "❌ Missing")
    timestamp = row.get("timestamp", "❓")
    report_url = f"{REPORT_BUCKET_URL}/{quote(report_key)}" if report_key != "❌ Missing" else None

    label = f"📌 {sid} — {timestamp}"
    with st.expander(label):
        st.write(f"**📧 Email**: {email}")
        st.write(f"**📝 Feedback Summary**: {feedback}")
        st.write(f"**🗂️ Report Key**: `{report_key}`")
        st.write(f"**📎 Report URL**: {report_url or '❌ Missing'}")

        if report_url:
            view_report_button("📥 View Report", report_url, sid, key_suffix=idx)
        else:
            st.warning("⚠️ Report URL is missing.")
