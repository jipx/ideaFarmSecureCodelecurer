
import streamlit as st
import requests
import time
import pandas as pd
import json

st.set_page_config(page_title="Secure Code Grading Dashboard", layout="centered")

st.title("📊 Grading Status Dashboard")

if "history" not in st.session_state:
    st.session_state.history = []

submission_id = st.text_input("Enter your Submission ID", "")

auto_refresh = st.checkbox("Auto-refresh status every 10 seconds")
show_raw = st.checkbox("Show raw API request and response")

def display_json_report(data: dict):
    st.subheader("📝 Secure Code Grading Report")
    st.markdown("---")

    st.write(f"**📌 Submission ID:** `{data.get('submission_id', 'N/A')}`")
    st.write(f"**📊 Status:** `{data.get('status', 'unknown').capitalize()}`")

    st.markdown("**💬 Feedback:**")
    st.info(data.get("feedback", "No feedback provided."), icon="💡")

    report_url = data.get("report_url")

    if report_url:
        st.markdown("**📥 Report Content:**")
        try:
            response = requests.get(report_url)
            response.raise_for_status()
            report_text = response.text

            try:
                parsed = json.loads(report_text)
                st.json(parsed)
            except json.JSONDecodeError:
                st.code(report_text, language="text")
        except Exception as e:
            st.error(f"⚠️ Failed to fetch report content: {e}")
    else:
        st.warning("No report URL available.")

    st.markdown("---")

    json_data = json.dumps(data, indent=2)
    st.download_button(
        label="📄 Download JSON Report Metadata",
        data=json_data,
        file_name=f"{data.get('submission_id', 'report')}.json",
        mime="application/json"
    )

if submission_id:
    def fetch_status():
        try:
            base_url = "https://u8w3qqosk4.execute-api.ap-northeast-1.amazonaws.com/prod"
            status_url = f"{base_url}/status?submission_id={submission_id}"
            response = requests.get(status_url)
            if show_raw:
                with st.expander("📡 Raw API Details"):
                    st.code(f"GET {status_url}", language="http")
                    st.code(response.text, language="json")

            if response.status_code == 200:
                result = response.json()
                result["status"] = "completed" if result.get("report_url") else "pending"
                return result
            else:
                st.error(f"❌ Error: {response.status_code} - {response.json().get('error', 'Unknown error')}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
        return None

    placeholder = st.empty()

    def render_status(result):
        if result:
            with placeholder.container():
                st.success(f"✅ Submission ID: {result['submission_id']}")
                display_json_report(result)

                st.session_state.history.append({
                    "ID": result["submission_id"],
                    "Status": result["status"],
                    "Feedback": result.get("feedback", ""),
                    "Report URL": result.get("report_url", "")
                })
                if len(st.session_state.history) > 50:
                    st.session_state.history = st.session_state.history[-50:]

    result = fetch_status()
    render_status(result)

    if auto_refresh and (not result or result["status"] != "completed"):
        for _ in range(60):
            time.sleep(10)
            result = fetch_status()
            render_status(result)
            if result and result["status"] == "completed":
                break

if st.session_state.history:
    st.markdown("## 🕘 Submission History")
    st.dataframe(st.session_state.history[::-1])

    csv = pd.DataFrame(st.session_state.history).to_csv(index=False)
    st.download_button("📤 Download History as CSV", csv, "grading_history.csv", "text/csv")
