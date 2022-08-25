# --no-window option when no window should be opened
import os
import subprocess
import sys

local = os.path.dirname(os.path.dirname(__file__))


subprocess.call(
    [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "--locals",
        "-s",
        local+"/game_tests/units",
        "-t",
        local,
    ]
)

