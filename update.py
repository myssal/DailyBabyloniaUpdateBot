import os
import json
import base64
import requests

OWNER = "myssal"
REPO = "PGR_Data"
BRANCH = "master"
FILE_PATH = "version.json"
GH_TOKEN = os.getenv("GH_TOKEN")

API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{FILE_PATH}"


def get_file_info():
    headers = {"Authorization": f"token {GH_TOKEN}"}
    resp = requests.get(API_URL, headers=headers, params={"ref": BRANCH})
    resp.raise_for_status()
    return resp.json()


def update_multiple(changes: dict):
    file_info = get_file_info()
    content = base64.b64decode(file_info["content"]).decode()
    data = json.loads(content)

    commit_lines = []
    for field, new_ver in changes.items():
        old_ver = data.get(field, "")
        if old_ver != new_ver:
            data[field] = new_ver
            commit_lines.append(f"- {field} [{old_ver}] -> [{new_ver}]")

    if not commit_lines:
        print("No changes to commit.")
        return

    new_content = json.dumps(data, indent=2, ensure_ascii=False)
    encoded = base64.b64encode(new_content.encode()).decode()

    payload = {
        "message": "feat: version changed.",
        "content": encoded,
        "sha": file_info["sha"],
        "branch": BRANCH,
        "committer": {
            "name": "myssal",
            "email": "143514975+myssal@users.noreply.github.com"
        }
    }

    headers = {"Authorization": f"token {GH_TOKEN}"}
    resp = requests.put(API_URL, headers=headers, json=payload)
    resp.raise_for_status()
    print("version updated:\n" + "\n".join(commit_lines))
