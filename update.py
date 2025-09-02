import os
import json
import base64
import requests

OWNER = "myssal"
REPO = "PGR_Data"
FILE_PATH = "version.json"
BRANCH = "master"

def get_file_info():
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{FILE_PATH}?ref={BRANCH}"
    headers = {"Authorization": f"token {os.getenv('GH_TOKEN')}"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

def update_file(new_cn_beta):
    file_info = get_file_info()

    content = base64.b64decode(file_info["content"]).decode()
    data = json.loads(content)

    old_ver = data.get("cn_beta")
    if old_ver == new_cn_beta:
        print("No change needed")
        return

    data["cn_beta"] = new_cn_beta
    new_content = json.dumps(data, indent=2, ensure_ascii=False)

    # encode back to base64
    encoded = base64.b64encode(new_content.encode()).decode()

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {os.getenv('GH_TOKEN')}"}
    payload = {
        "message": f"feat: cn_beta version  [{old_ver}] → [{new_cn_beta}]",
        "content": encoded,
        "sha": file_info["sha"],
        "branch": BRANCH,
        "committer": {
            "name": "myssal",
            "email": "143514975+myssal@users.noreply.github.com"
        },
        "author": {
            "name": "myssal",
            "email": "143514975+myssal@users.noreply.github.com"
        }
    }

    r = requests.put(url, headers=headers, data=json.dumps(payload))
    r.raise_for_status()
    print(f"feat: cn_beta version  [{old_ver}] → [{new_cn_beta}]")
