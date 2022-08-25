# --no-window option when no window should be opened
import os
import subprocess
import sys

local = os.path.dirname(os.path.dirname(__file__))


code = subprocess.call(
    [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "--locals",
        "-s",
        local + "/game_tests/units",
        "-t",
        local,
    ]
)


if code != 0:
    sys.exit(code)
