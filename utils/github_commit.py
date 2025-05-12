import os
import json
import base64
import requests

def push_df_to_github(
    df,
    user,
    repo,
    path,
    commit_message="Auto-upload from Colab",
    branch="main"
):
    """
    Push a DataFrame to GitHub as a CSV file using GitHub's REST API.

    Args:
        df: DataFrame to push
        user: GitHub username
        repo: Repository name
        path: File path in the repo (e.g. 'data/processed/st53_cleaned.csv')
        commit_message: GitHub commit message
        branch: Target branch (default: 'main')
    """

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("Missing GitHub token. Set it with os.environ['GITHUB_TOKEN'].")

    # Encode DataFrame as base64 CSV
    csv_bytes = df.to_csv(index=False).encode()
    csv_base64 = base64.b64encode(csv_bytes).decode()

    # Prepare request headers and endpoint
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    url = f"https://api.github.com/repos/{user}/{repo}/contents/{path}"

    # Check if file exists (get SHA for overwrite)
    response = requests.get(url, headers=headers)
    sha = response.json().get("sha") if response.status_code == 200 else None

    # Prepare PUT request payload
    payload = {
        "message": commit_message,
        "content": csv_base64,
        "branch": branch
    }
    if sha:
        payload["sha"] = sha

    # Push to GitHub
    res = requests.put(url, headers=headers, data=json.dumps(payload))

    if res.status_code in [200, 201]:
        print(f"✅ File pushed to GitHub: https://github.com/{user}/{repo}/blob/{branch}/{path}")
    else:
        print("❌ GitHub push failed:", res.json())
