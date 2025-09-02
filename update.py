import os
import json
import base64
import requests

OWNER = "myssal"
REPO = "PGR_Data"
BRANCH = "main"
FILE_PATH = "version.json"
GH_TOKEN = os.getenv("GH_TOKEN")

API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{FILE_PATH}"


def get_file_info():
    headers = {"Authorization": f"token {GH_TOKEN}"}
    resp = requests.get(API_URL, headers=headers, params={"ref": BRANCH})
    resp.raise_for_status()
    return resp.json()


def update_file(new_ver, field="cn_beta"):
    # update specific field in version.json
    file_info = get_file_info()
    content = base64.b64decode(file_info["content"]).decode()
    data = json.loads(content)

    data[field] = new_ver

    new_content = json.dumps(data, indent=2, ensure_ascii=False)
    encoded = base64.b64encode(new_content.encode()).decode()

    payload = {
        "message": f"Update {field}: {new_ver}",
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
    print(f"{field} updated to {new_ver}")
