import json
import os
import subprocess
import sys
import requests
import zipfile

with open("./config.json") as f:
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

asset_url = data["mc target"]["version url"]
asset_request = requests.get(asset_url)

os.makedirs("../cache", exist_ok=True)
with open("../cache/assets_tmp.zip", mode="wb") as f:
    f.write(asset_request.content)

print("[INFO] filtering assets")

if os.path.exists("../cache/assets.zip"):
    os.remove("../cache/assets.zip")

with zipfile.ZipFile("../cache/assets_tmp.zip") as fr, zipfile.ZipFile(
    "../cache/assets.zip", mode="w"
) as fw:
    for file in fr.namelist():
        if not file.endswith(".class"):
            with fw.open(file, mode="w") as fi:
                fi.write(fr.read(file))

print("[INFO] cleaning up")

os.remove("../cache/assets_tmp.zip")
