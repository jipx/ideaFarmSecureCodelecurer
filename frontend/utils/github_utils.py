import base64
import requests
from github import Github
import uuid
from datetime import datetime

def upload_code_to_github(files, repo_name, token, student_id):
    g = Github(token)
    repo = g.get_repo(repo_name)
    branch_name = f"feature/scan-{student_id}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    main_sha = repo.get_branch("main").commit.sha
    repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_sha)

    for path, content in files.items():
        repo.create_file(
            path=f"{branch_name}/{path}",
            message=f"Scan: {path}",
            content=content,
            branch=branch_name
        )
    return branch_name

def get_codeql_alerts(repo_name, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    url = f"https://api.github.com/repos/{repo_name}/code-scanning/alerts"
    for _ in range(10):
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200 and resp.json():
            return resp.json()
        import time; time.sleep(10)
    return []

def fetch_code_snippet(repo, token, path, line, context=2):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        content = r.json().get("content")
        if content:
            decoded = base64.b64decode(content).decode("utf-8", errors="ignore")
            lines = decoded.splitlines()
            start = max(0, line - context - 1)
            end = min(len(lines), line + context)
            return "\n".join(lines[start:end])
    return "Unable to fetch snippet"
