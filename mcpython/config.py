from __future__ import annotations

import math
import pathlib

TICKS_PER_SEC = 20
WALKING_SPEED = 5
FLYING_SPEED = 15
GRAVITY = 20.0
MAX_JUMP_HEIGHT = 1.0  # About the height of a block.
JUMP_SPEED = math.sqrt(2 * GRAVITY * MAX_JUMP_HEIGHT)
TERMINAL_VELOCITY = 50
PLAYER_HEIGHT = 2

TMP = pathlib.Path(__file__).parent.parent.joinpath("cache/temp")
TMP.mkdir(parents=True, exist_ok=True)
