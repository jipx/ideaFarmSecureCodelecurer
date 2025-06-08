import streamlit as st
import json

import os
import sys

# Dynamically add the parent directory to the path so 'utils' can be imported
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
UTILS_DIR = os.path.join(PARENT_DIR, "utils")

if UTILS_DIR not in sys.path:
    sys.path.insert(0, UTILS_DIR)

# Now import the utilities



from utils.zip_utils import extract_files
from utils.github_utils import upload_code_to_github, get_codeql_alerts, fetch_code_snippet
from utils.download_utils import download_repo_zip

st.set_page_config(page_title="CodeQL Vulnerability Scanner", layout="wide")
st.title("🔍 Streamlit + GitHub CodeQL Vulnerability Scanner")

input_method = st.radio("Select Input Method", ["Upload ZIP", "GitHub URL"])
repo_name = st.text_input("📉 Target GitHub Repo (e.g., username/repo)", value="jipx/codeql-submissions")
token = st.secrets.get("github", {}).get("github_token")

if not token:
    token = st.text_input("🔐 GitHub Token", type="password")
student_id = st.text_input("Enter your Student ID", value="jipx901", max_chars=20)

alerts = []

if input_method == "Upload ZIP":
    uploaded_file = st.file_uploader("Upload your source code as ZIP", type=["zip"])
    if uploaded_file and repo_name and token and student_id and st.button("🚀 Scan with CodeQL"):
        files = extract_files(uploaded_file)
        st.info(f"📂 Uploading {len(files)} files to GitHub...")
        branch = upload_code_to_github(files, repo_name, token, student_id)
        st.success(f"💼 Code pushed to branch `{branch}`")

        st.info("⏳ Waiting for CodeQL scan...")
        with st.spinner("Analyzing with CodeQL..."):
            alerts = get_codeql_alerts(repo_name, token)

elif input_method == "GitHub URL":
    github_url = st.text_input("Paste public GitHub repo URL (e.g. https://github.com/user/repo)")
    if github_url and repo_name and token and student_id and st.button("🔍 Scan GitHub Repo"):
        zip_file = download_repo_zip(github_url)
        if zip_file:
            files = extract_files(zip_file)
            st.info(f"📂 Extracted {len(files)} source files.")
            branch = upload_code_to_github(files, repo_name, token, student_id)
            st.success(f"💼 Code from GitHub URL pushed to `{branch}`")

            st.info("⏳ Waiting for CodeQL scan...")
            with st.spinner("Analyzing with CodeQL..."):
                alerts = get_codeql_alerts(repo_name, token)
        else:
            st.error("❌ Failed to fetch GitHub repository ZIP")

if alerts:
    st.success(f"✅ {len(alerts)} issues found.")
    for alert in alerts:
        rule = alert['rule']
        inst = alert['most_recent_instance']
        path = inst['location']['path']
        line = inst['location']['start_line']

        st.markdown(f"### 🛡️ {rule['description']}")
        st.write(f"- **Severity**: {rule['severity']}")
        st.write(f"- **CWE**: {rule.get('cwe_id', 'N/A')}")
        st.write(f"- **Location**: `{path}` at line {line}")

        snippet = fetch_code_snippet(repo_name, token, path, line, context=2)
        snippet_lines = snippet.splitlines()
        alert['code_snippet'] = snippet_lines
        st.code("\n".join(snippet_lines), language="python")

        alert['shield'] = {
            "badge": f"🛡️ {rule.get('owasp_category', 'Unknown')}",
            "severity_color": "red" if rule['severity'].lower() == "critical" else "orange" if rule['severity'].lower() == "high" else "yellow",
            "cwe_badge": rule.get('cwe', 'N/A'),
            "owasp_badge": rule.get('owasp_category', 'Axx'),
            "score": 85
        }

    st.download_button("Download Findings JSON", json.dumps(alerts, indent=2), "codeql_alerts.json")
else:
    st.warning("⚠️ No findings returned or scan in progress. Please retry later.")

st.markdown("### 📊 View Grading Status")
with st.expander("Click to view latest scan status"):
    if st.button("🔁 Refresh Status"):
        st.rerun()
    if 'branch' in locals():
        st.success(f"Check scan results on GitHub under branch: `{branch}`")
    else:
        st.info("Upload code to GitHub to generate a scan branch.")

st.markdown("---")
st.markdown("[➡️ Go to Upload Page](./upload_signed_url)", unsafe_allow_html=True)
