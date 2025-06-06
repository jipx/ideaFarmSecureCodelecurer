import streamlit as st
import requests
import time
import json

st.set_page_config(page_title="📋 Branch Scan Status", layout="wide")
st.title("📋 GitHub Branch Scan Status Overview")

repo_name = st.text_input("🔎 Enter GitHub Repo (e.g., username/repo):", value="jipx/codeql-submissions")
token = st.secrets["github"].get("github_token") if "github" in st.secrets else st.text_input("🔐 GitHub Token", type="password")

auto_refresh = st.checkbox("🔄 Auto-refresh every 30 seconds")

def delete_branch(repo, branch, headers):
    api_url = f"https://api.github.com/repos/{repo}/git/refs/heads/{branch}"
    response = requests.delete(api_url, headers=headers)
    return response.status_code == 204

def fetch_branch_status(repo_name, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    branches_url = f"https://api.github.com/repos/{repo_name}/branches"
    branches_res = requests.get(branches_url, headers=headers)
    branch_info = []

    if branches_res.status_code == 200:
        branches = branches_res.json()
        for branch in branches:
            name = branch['name']
            runs_url = f"https://api.github.com/repos/{repo_name}/actions/workflows/codeql.yml/runs?branch={name}&per_page=1"
            runs_res = requests.get(runs_url, headers=headers)

            status, conclusion, updated = "N/A", "N/A", "N/A"
            if runs_res.status_code == 200:
                runs_data = runs_res.json()
                if runs_data.get("workflow_runs"):
                    run = runs_data["workflow_runs"][0]
                    status = run["status"]
                    conclusion = run["conclusion"] or "in progress"
                    updated = run["updated_at"]

            alert_link = None
            report_url = None
            if conclusion == "success":
                alert_link = (
                    f"https://github.com/{repo_name}/security/code-scanning"
                    f"?query=is%3Aopen+branch%3Amain+branch%3A{name.replace('/', '%2F')}"
                )
                branch_sanitized = name.replace("feature/", "")
                report_url = (
                    f"https://raw.githubusercontent.com/{repo_name}/refs/heads/{name}/sarif_reports/{branch_sanitized}/scan-{branch_sanitized}.sarif.json"
                )

            branch_info.append({
                "branch": name,
                "student_id": name.split('-')[1] if "scan-" in name else "N/A",
                "status": "in_progress" if status == "N/A" else status,
                "conclusion": "in progress" if conclusion == "N/A" else conclusion,
                "updated": updated,
                "alert_link": alert_link,
                "report_url": report_url
            })
    return branch_info

def get_row_style(conclusion):
    if conclusion == "success":
        return "background-color:#d4edda; padding: 8px; border-radius: 6px"
    elif conclusion == "failure":
        return "background-color:#f8d7da; padding: 8px; border-radius: 6px"
    elif conclusion == "in_progress" or conclusion == "N/A":
        return "background-color:#fff3cd; padding: 8px; border-radius: 6px"
    else:
        return "padding: 8px"

def get_codeql_alerts(repo_name, token, branch):
    url = f"https://api.github.com/repos/{repo_name}/code-scanning/alerts?ref={branch}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json()
    return []

def fetch_code_snippet(repo_name, token, path, branch, start_line, context=2):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.raw"
    }
    url = f"https://api.github.com/repos/{repo_name}/contents/{path}?ref={branch}"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        lines = res.text.splitlines()
        start = max(0, start_line - context - 1)
        end = min(len(lines), start_line + context)
        return '\n'.join(lines[start:end])
    return "❌ Failed to fetch snippet."

if repo_name and token:
    branch_data = fetch_branch_status(repo_name, token)
    if branch_data:
        st.write("### ✅ Select branches to delete:")
        selected_branches = []
        for branch in branch_data:
            style = get_row_style(branch['conclusion'])
            cb = st.checkbox(f"Select `{branch['branch']}`", key=f"select_{branch['branch']}")
            if cb:
                selected_branches.append(branch['branch'])

            gif_html = '<img src="images/inprogress.gif" width="30" alt="Loading">' if branch['conclusion'] == 'in_progress' else ""
            alert_html = f"<br>📅 <a href='{branch['alert_link']}' target='_blank'>CodeQL Alerts</a>" if branch['alert_link'] else ""
            report_html = f"<br>📄 <a href='{branch['report_url']}' target='_blank'>Download SARIF</a>" if branch['report_url'] else ""

            st.markdown(f"""
<div style='{style}'>
  <strong>{branch['branch']}</strong> | Student: {branch['student_id']}<br>
  Status: {branch['status']} | Conclusion: {branch['conclusion']} | Updated: {branch['updated']} {gif_html}{alert_html}{report_html}
</div>
""", unsafe_allow_html=True)

            if branch['conclusion'] == "success":
                if st.button(f"🔍 View Findings: {branch['branch']}", key=f"view_{branch['branch']}"):
                    findings = get_codeql_alerts(repo_name, token, branch['branch'])
                    st.download_button(
                        label=f"📥 Download {branch['branch']} Alerts",
                        data=json.dumps(findings, indent=2),
                        file_name=f"{branch['branch']}_alerts.json",
                        mime="application/json"
                    )
                    for finding in findings:
                        message = finding.get("rule", {}).get("description", "No description")
                        location = finding.get("most_recent_instance", {}).get("location", {})
                        file = location.get("path", "")
                        line = location.get("start_line", 0)
                        st.markdown(f"**Issue**: {message}")
                        st.markdown(f"📄 File: `{file}` | Line: {line}")
                        snippet = fetch_code_snippet(repo_name, token, file, branch['branch'], line)
                        st.code(snippet, language="python")

                    st.markdown(f"### 🧾 Embedded SARIF Report for `{branch['branch']}`")
                    st.components.v1.iframe(branch['report_url'], height=400)

        if selected_branches:
            if st.button("🗑️ Confirm Delete Selected Branches"):
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json"
                }
                for branch_name in selected_branches:
                    if delete_branch(repo_name, branch_name, headers):
                        st.success(f"✅ Deleted: {branch_name}")
                    else:
                        st.error(f"❌ Failed to delete: {branch_name}")
                st.rerun()
        else:
            st.info("ℹ️ Select branches above to delete.")
    else:
        st.warning("⚠️ No branches or scan data found.")

    if auto_refresh:
        st.info("🔄 Auto-refresh enabled. Page will update every 30 seconds.")
        time.sleep(30)
        st.rerun()
