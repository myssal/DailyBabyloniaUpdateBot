import json
import urllib.request
import base64
import update

# cdn config
CONFIGS = {
    "EN": {
        "cdn": "http://prod-encdn-volcdn.kurogame.net/prod",
        "token": "",
        "appId": "/com.kurogame.punishing.grayraven.en",
        "platform": "android",
    },
    "EN_PC": {
        "cdn": "http://prod-encdn-volcdn.kurogame.net/prod",
        "token": "",
        "appId": "/com.kurogame.punishing.grayraven.en.pc",
        "platform": "standalone",
    },

    "KR": {
        "cdn": "http://prod-krcdn-volcdn.kurogame.net/prod",
        "token": "",
        "appId": "/com.herogame.punishing.grayraven.kr",
        "platform": "android",
    },
    "KR_PC": {
        "cdn": "http://prod-krcdn-volcdn.kurogame.net/prod",
        "token": "",
        "appId": "/com.herogame.pc.punishing.grayraven.kr",
        "platform": "standalone",
    },

    "JP": {
        "cdn": "http://prod-jpcdn-volcdn.kurogame.net/prod",
        "token": "",
        "appId": "/com.herogame.gplay.punishing.grayraven.jp",
        "platform": "android",
    },
    "JP_PC": {
        "cdn": "http://prod-jpcdn-volcdn.kurogame.net/prod",
        "token": "",
        "appId": "/com.herogame.pc.punishing.grayraven.jp",
        "platform": "standalone",
    },

    "TW": {
        "cdn": "http://prod-twcdn-volcdn.kurogame.net/prod",
        "token": "",
        "appId": "/com.herogame.gplay.punishing.grayraven.tw",
        "platform": "android",
    },
    "TW_PC": {
        "cdn": "http://prod-twcdn-volcdn.kurogame.net/prod",
        "token": "",
        "appId": "/com.herogame.pc.punishing.grayraven.tw",
        "platform": "standalone",
    },

    "CN": {
        "cdn": "http://prod-zspns-volccdn.kurogame.com/prod",
        "token": "EGE2QCJHK7MoHFBn",
        "appId": "/com.kurogame.haru.kuro",
        "platform": "android",
    },
    "CN_PC": {
        "cdn": "http://prod-zspns-volccdn.kurogame.com/prod",
        "token": "EGE2QCJHK7MoHFBn",
        "appId": "/com.kurogame.haru.kuro",
        "platform": "standalone",
    },

    "CN_BETA": {
        "cdn": "http://pre-zspns-volccdn.kurogame.com/pre",
        "token": "0B6CFEBaFE9OyvUc",
        "appId": "/com.kurogame.haru.pioneer",
        "platform": "android",
    },
    "CN_PC_BETA": {
        "cdn": "http://pre-zspns-volccdn.kurogame.com/pre",
        "token": "0B6CFEBaFE9OyvUc",
        "appId": "/com.kurogame.haru.pioneer",
        "platform": "standalone",
    },
}


def build_url(cdn, token, appId, version, platform):
    return f"{cdn}/client/config/{token}{appId}/{version}/{platform}/config.tab"


def fetch_config(cdn, token, appId, version, platform):
    url = build_url(cdn, token, appId, version, platform)
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return resp.read().decode()
    except Exception:
        return None


def parse_document_version(text):
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) >= 3 and parts[0] == "DocumentVersion":
            return parts[2].strip()
    return None


def bump_version(base_ver, cdn, token, appId, platform):
    parts = [int(x) for x in base_ver.split(".")]
    x, y, z = parts

    # bump minor version
    new_y = f"{x}.{y+1}.0"
    if fetch_config(cdn, token, appId, new_y, platform):
        return new_y

    # bump major version, either x+1.0.0 or x+1.1.0
    new_x0 = f"{x+1}.0.0"
    new_x1 = f"{x+1}.1.0"

    if fetch_config(cdn, token, appId, new_x0, platform):
        return new_x0
    if fetch_config(cdn, token, appId, new_x1, platform):
        return new_x1

    # some servers like tw, kr, jp still haven't caught up with cn progress.
    # this will check one more version to ensure bot get correct version.
    # 3.6 = crepuscule, 3.8 = aegis
    if (x,y) == (3,6):
        new_y2 = f"{x}.{y + 2}.0"
        if fetch_config(cdn, token, appId, new_y2, platform):
            return new_y2

    return None


def main():
    # load current version.json
    file_info = update.get_file_info()
    pub_data = json.loads(base64.b64decode(file_info["content"]).decode())

    changed = {}

    for key, cfg in CONFIGS.items():
        old_doc_ver = pub_data.get(key)
        if not old_doc_ver:
            print(f"Skipping {key}: no version in version.json")
            continue

        parts = old_doc_ver.split(".")
        base_ver = f"{parts[0]}.{parts[1]}.0"

        text = None
        doc_ver = None

        # try bumped version
        bumped = bump_version(
            base_ver,
            cfg["cdn"],
            cfg["token"],
            cfg["appId"],
            cfg["platform"]
        )

        if bumped:
            text = fetch_config(
                cfg["cdn"],
                cfg["token"],
                cfg["appId"],
                bumped,
                cfg["platform"]
            )

            if text:
                doc_ver = parse_document_version(text)
                print(f"{key}: bumped version ({bumped}), DocumentVersion={doc_ver}")

                if doc_ver and doc_ver.endswith(".0"):
                    print(f"{key}: ignore bumped .0 version, fallback to base")
                    text = None
                    doc_ver = None

        # fallback to base
        if not text:
            text = fetch_config(
                cfg["cdn"],
                cfg["token"],
                cfg["appId"],
                base_ver,
                cfg["platform"]
            )

            if text:
                doc_ver = parse_document_version(text)
                print(f"{key}: base version ({base_ver}), DocumentVersion={doc_ver}")

        if not text or not doc_ver:
            print(f"{key}: no valid DocumentVersion")
            continue

        if doc_ver.endswith(".0"):
            print(f"{key}: ignored (.0 only)")
            continue

        if doc_ver != old_doc_ver:
            print(f"{key}: UPDATED {old_doc_ver} -> {doc_ver}")
            changed[key] = doc_ver
        else:
            print(f"{key}: no change")

    # push updates
    if changed:
        update.update_multiple(changed)
    else:
        print("no updates detected")


if __name__ == "__main__":
    main()