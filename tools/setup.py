import json
import os
import subprocess
import sys
import zipfile


local = os.path.dirname(os.path.dirname(__file__))

with open(local+"/tools/config.json") as f:
    data = json.load(f)

print("[INFO] installing dependencies")

subprocess.call(
    [
        sys.executable,
        "-m",
        "pip",
        "install",
        # "--user",
        "-r",
        "../requirements.txt",
    ]
)

if data["is development environment"]:
    print("[INFO] installing dependencies (dev)")

    subprocess.call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            # "--user",
            "-r",
            "../requirements_dev.txt",
        ]
    )

print("[INFO] downloading assets")

# This belongs here as it is installed above
import requests

asset_url = data["mc target"]["version url"]
asset_request = requests.get(asset_url)

os.makedirs(local+"/cache", exist_ok=True)
with open(local+"/cache/assets_tmp.zip", mode="wb") as f:
    f.write(asset_request.content)

print("[INFO] filtering assets")

if os.path.exists(local+"/cache/assets.zip"):
    os.remove(local+"/cache/assets.zip")

with zipfile.ZipFile(local+"/cache/assets_tmp.zip") as fr, zipfile.ZipFile(
    local+"/cache/assets.zip", mode="w"
) as fw:
    for file in fr.namelist():
        if not file.endswith(".class"):
            with fw.open(file, mode="w") as fi:
                fi.write(fr.read(file))

print("[INFO] cleaning up")

os.remove(local+"/cache/assets_tmp.zip")
