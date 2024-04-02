from __future__ import annotations

import itertools
import random
import typing

import numpy
import opensimplex

if typing.TYPE_CHECKING:
    from mcpython.world.World import Chunk


# base height noise
noise = opensimplex.OpenSimplex(random.randint(0, 1 << 256))
# height noise modifier
noise2 = opensimplex.OpenSimplex(random.randint(0, 1 << 256))
# height noise range modifier
noise3 = opensimplex.OpenSimplex(random.randint(0, 1 << 256))
# height noise offset modifier
noise4 = opensimplex.OpenSimplex(random.randint(0, 1 << 256))
# river depth noise
noise5 = opensimplex.OpenSimplex(random.randint(0, 1 << 256))
# river creation modifier
noise6 = opensimplex.OpenSimplex(random.randint(0, 1 << 256))
# river base influence modifier
noise7 = opensimplex.OpenSimplex(random.randint(0, 1 << 256))


def generate_chunk(chunk: Chunk):
    cx, cz = chunk.position

    # height = noise.noise2array(
    #     numpy.arange(cx * 16, cx * 16 + 16) / 60,
    #     numpy.arange(cz * 16, cz * 16 + 16) / 60,
    # )

    for dx, dz in itertools.product(range(16), range(16)):
        x = cx * 16 + dx
        z = cz * 16 + dz
        hn: float = noise.noise3(
            x / 60,
            z / 60,
            x * z * noise2.noise2(x / 1000, z / 1000) / 100,
        )
        bn: float = noise3.noise2(
            x / 200,
            z / 200,
        )
        vn: float = noise4.noise2(
            x / 200,
            z / 200,
        )
        rd: float = noise5.noise2(x / 400, z / 400)
        h = (hn / 2 + 0.5) * (15 + bn * 3) + (30 + vn * 5)
        if 0.3 <= rd <= 0.35:
            q = noise6.noise2(x / 200, z / 200)
            if q >= 0:
                q = min(q * 10, 1)
                # Carve a revine at most 16 blocks deep, deepest in the middle
                rd = (0.5 - abs((rd - 0.3) * 20 - 0.5)) * 2 * 16
                v = (noise7.noise2(x / 200, z / 200) / 2 + 0.5) / 2 + 0.25
                h = (
                    (h - rd) * v + ((15 + bn * 3) + (30 + vn * 5) - 10) * (1 - v)
                ) * q + h * (1 - q)

        h = int(h)

        chunk.world.add_block(
            (x, 0, z), "minecraft:bedrock", immediate=False, block_update=False
        )

        for y in range(1, h - 4):
            chunk.world.add_block(
                (x, y, z), "minecraft:stone", immediate=False, block_update=False
            )

        for y in range(h - 4, h):
            chunk.world.add_block(
                (x, y, z), "minecraft:dirt", immediate=False, block_update=False
            )