from __future__ import annotations

import itertools
import random
import typing
import cProfile

import opensimplex

if typing.TYPE_CHECKING:
    from mcpython.world.World import Chunk, World


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

bedrock_noise = opensimplex.OpenSimplex(random.randint(0, 1 << 256))

dirt_height_noise = opensimplex.OpenSimplex(random.randint(0, 1 << 256))
grass_noise = opensimplex.OpenSimplex(random.randint(0, 1 << 256))


ORES = [
    "minecraft:coal_ore",
    "minecraft:iron_ore",
    "minecraft:diamond_ore",
    "minecraft:gold_ore",
    "minecraft:lapis_ore",
]


# PROFILE = cProfile.Profile()


class Structure:
    def place(self, world: World, position: tuple[int, int, int], rng: random.Random):
        raise NotImplementedError


class OakTree:
    def __init__(
        self,
        stem: str,
        leaves: str,
        stem_range=range(4, 6),
        leave_height_range=range(3, 6),
        leave_height_offset=range(1, 2),
        leave_size=range(3, 4),
    ):
        self.stem = stem
        self.leaves = leaves
        self.stem_range = stem_range
        self.leave_height_range = leave_height_range
        self.leave_height_offset = leave_height_offset
        self.leave_size = leave_size

    def place(self, world: World, position: tuple[int, int, int], rng: random.Random):
        x, y, z = position
        height = rng.randrange(self.stem_range.start, self.stem_range.stop + 1)

        leave_height = rng.randrange(
            self.leave_height_range.start, self.leave_height_range.stop + 1
        )
        leave_offset = rng.randrange(
            self.leave_height_offset.start, self.leave_height_offset.stop + 1
        )
        leave_size = rng.randrange(self.leave_size.start, self.leave_size.stop + 1)

        for dy in range(leave_height):
            ry = y + dy - leave_offset + height
            for dx in range(-leave_size, leave_size + 1):
                for dz in range(-leave_size, leave_size + 1):
                    if dx * dx + dz * dz + dy * dy > leave_size * leave_size:
                        continue
                    world.add_block(
                        (x + dx, ry, z + dz),
                        self.leaves,
                        immediate=False,
                        block_update=False,
                    )

        for dy in range(height):
            world.add_block(
                (x, y + dy, z), self.stem, immediate=False, block_update=False
            )


OAK_TREE = OakTree("minecraft:oak_log", "minecraft:oak_leaves")


def generate_chunk(chunk: Chunk):
    #     PROFILE.enable()
    #     _generate_chunk(chunk)
    #     PROFILE.disable()
    #     PROFILE.print_stats("cumulative")
    #
    #
    # def _generate_chunk(chunk: Chunk):
    cx, cz = chunk.position
    heightmap: dict[tuple[int, int], int] = {}

    r = random.Random(random.randint(1, 1 << 256))

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
        heightmap[x, z] = h

        chunk.add_block(
            (x, 0, z), "minecraft:bedrock", immediate=False, block_update=False
        )

        for y in range(1, h - 4):
            chunk.add_block(
                (x, y, z), "minecraft:stone", immediate=False, block_update=False
            )

        for y in range(h - 6 - int(2 * dirt_height_noise.noise2(x / 20, z / 20)), h):
            chunk.add_block(
                (x, y, z), "minecraft:dirt", immediate=False, block_update=False
            )

        chunk.add_block(
            (x, h, z), "minecraft:grass_block", immediate=False, block_update=False
        )

        # if grass_noise.noise2(x / 10, z / 10) < 0.3:
        #     chunk.add_block(
        #         (x, h + 1, z),
        #         "minecraft:short_grass",
        #         immediate=False,
        #         block_update=False,
        #     )

        for y in range(1, 4):
            if bedrock_noise.noise3(x, y, z) >= 0:
                chunk.add_block(
                    (x, y, z), "minecraft:bedrock", immediate=False, block_update=False
                )

    for _ in range(r.randint(200, 800)):
        ore = r.choice(ORES)
        pos = (
            r.randrange(cx * 16, cx * 16 + 16),
            r.randrange(0, 256),
            r.randrange(cz * 16, cz * 16 + 16),
        )
        block = chunk.blocks.get(pos)
        if block and block.NAME == "minecraft:stone":
            chunk.add_block(pos, ore, immediate=False, block_update=False)

    while r.random() <= 0.2:
        x, z = r.randrange(cx * 16, cx * 16 + 16), r.randrange(cz * 16, cz * 16 + 16)
        y = heightmap[x, z]
        OAK_TREE.place(chunk.world, (x, y + 1, z), r)
