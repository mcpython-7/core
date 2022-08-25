import subprocess
import sys

print("[INFO] running black code formatter")

subprocess.call([sys.executable, "-m", "black", ".."])
