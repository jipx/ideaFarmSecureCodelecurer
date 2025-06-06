
import requests
import io

def download_repo_zip(github_url):
    parts = github_url.strip("/").split("/")
    if len(parts) < 2:
        return None
    user, repo = parts[-2], parts[-1]
    zip_url = f"https://github.com/{user}/{repo}/archive/refs/heads/main.zip"
    r = requests.get(zip_url)
    if r.status_code == 200:
        return io.BytesIO(r.content)
    return None
