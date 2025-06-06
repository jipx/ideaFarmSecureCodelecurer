import streamlit as st
import requests
import time

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

            branch_info.append({
                "branch": name,
                "student_id": name.split('-')[1] if "scan-" in name else "N/A",
                "status": "in_progress" if status == "N/A" else status,
                "conclusion": "in progress" if conclusion == "N/A" else conclusion,
                "updated": updated,
                "alert_link": f"https://github.com/{repo_name}/security/code-scanning?query=is:open+ref:refs/heads/{name}"
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

            st.markdown(f"""
<div style='{style}'>
  <strong>{branch['branch']}</strong> | Student: {branch['student_id']}<br>
  Status: {branch['status']} | Conclusion: {branch['conclusion']} | Updated: {branch['updated']} {gif_html}<br>
  📥 <a href='{branch['alert_link']}' target='_blank'>CodeQL Alerts</a>
</div>
""", unsafe_allow_html=True)

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
