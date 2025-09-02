import json
import urllib.request
from pathlib import Path
import update

CUR_VER_FILE = Path("current_ver.json")

def read_json(path):
    if path.exists():
        return json.loads(path.read_text())
    return {}

def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def build_url(version):
    return f"http://dev-zspns-volccdn.kurogame.com/dev/client/config/com.kurogame.haru.pioneer/{version}/android/config.tab"

def fetch_config(version):
    url = build_url(version)
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return resp.read().decode()
    except:
        return None

def parse_document_version(text):
    for line in text.splitlines():
        parts = line.split("\t")
        if parts[0] == "DocumentVersion":
            return parts[2].strip()
    return None

def bump_version(ver: str):
    """Increment y first, then x"""
    parts = [int(x) for x in ver.split(".")]
    x, y, z = parts
    # bump y
    new_y = f"{x}.{y+1}.0"
    if fetch_config(new_y):
        return new_y
    # bump x
    new_x0 = f"{x+1}.0.0"
    new_x1 = f"{x+1}.1.0"
    if fetch_config(new_x0):
        return new_x0
    if fetch_config(new_x1):
        return new_x1
    return None

def main():
    cur = read_json(CUR_VER_FILE)
    current_ver = cur.get("version", "3.8.0")

    text = fetch_config(current_ver)
    if not text:
        bumped = bump_version(current_ver)
        if not bumped:
            print("No new version found")
            return
        current_ver = bumped
        write_json(CUR_VER_FILE, {"version": current_ver})
        text = fetch_config(current_ver)

    doc_ver = parse_document_version(text)
    if not doc_ver:
        print("No DocumentVersion found")
        return

    # Get current public version from version.json in public repo
    file_info = update.get_file_info()
    pub_data = json.loads(
        __import__("base64").b64decode(file_info["content"]).decode()
    )
    old_ver = pub_data.get("cn_beta")

    if doc_ver != old_ver:
        print(f"New cn_beta DocumentVersion {doc_ver} (old {old_ver})")
        update.update_file(doc_ver)
    else:
        print("No change")

if __name__ == "__main__":
    main()
