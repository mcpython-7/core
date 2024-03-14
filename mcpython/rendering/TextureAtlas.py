from __future__ import annotations

import math

import PIL.Image
import pyglet

from mcpython.resources.ResourceManager import ResourceManager
from mcpython import config


class AtlasReference:
    def __init__(
        self,
        atlas: TextureAtlas,
        position: tuple[float, float],
        size: tuple[float, float],
    ):
        self.atlas = atlas
        self.position = position
        self.size = size

    def uv_section(self, uv: tuple[float, ...]) -> AtlasReference:
        if uv == (0, 0, 1, 1):
            return self
        a, b, c, d = uv
        x, y = self.position
        dx, dy = self.size
        sx, sy = self.atlas.size
        return AtlasReference(
            self.atlas, (x + a / sx, y + b / sy), ((c - a) * dx, (d - b) * dy)
        )

    def tex_coord(self) -> tuple[float, ...]:
        """Return the bounding vertices of the texture square."""
        mx, my = self.atlas.size
        dx = self.position[0] / mx
        dy = self.position[1] / my
        # fmt: off
        return (
            dx, dy, dx + self.size[0] / mx / self.atlas.block_size[0], dy, dx + self.size[0] / mx / self.atlas.block_size[0], dy + self.size[1] / my / self.atlas.block_size[1],  # Triangle 1
            dx, dy, dx + self.size[0] / mx / self.atlas.block_size[0], dy + self.size[1] / my / self.atlas.block_size[1], dx, dy + self.size[1] / my / self.atlas.block_size[1],  # Triangle 2
        )
        # fmt: on

    def get_texture(self) -> pyglet.image.AbstractImage:
        texture = self.atlas.get_texture()
        x, y = self.position
        dx, dy = self.size
        sx, sy = self.atlas.block_size
        return texture.get_region(x * sx, y * sy, sx, sy)


class TextureAtlas:
    def __init__(
        self,
        start_size: tuple[int, int] = (8, 8),
        block_size: tuple[int, int] = (16, 16),
    ):
        self.size = start_size
        self.block_size = block_size
        self.image = PIL.Image.new(
            "RGBA",
            (start_size[0] * block_size[0], start_size[1] * block_size[1]),
            (0, 0, 0, 0),
        )
        self.free_slots: list[tuple[tuple[int, int], tuple[int, int]]] = [
            ((0, 0), start_size)
        ]
        self._cache: dict[str, AtlasReference] = {}
        self._texture_cache = None

    def add_image_from_path(self, path: str) -> AtlasReference:
        # <namespace>:<file>.png
        if ":" in path:
            path = "assets/{}/textures/{}.png".format(*path.split(":"))

        if path in self._cache:
            return self._cache[path]

        reference = self.add_image(ResourceManager.load_pillow_image(path))
        self._cache[path] = reference
        return reference

    def add_image(self, image: PIL.Image.Image) -> AtlasReference:
        size = image.size
        blocks = math.ceil(size[0] / self.block_size[0]), math.ceil(
            size[1] / self.block_size[1]
        )

        for i, (location, free_size) in enumerate(self.free_slots):
            if free_size[0] >= blocks[0] and free_size[1] >= blocks[1]:
                self.free_slots.pop(i)
                reference = AtlasReference(self, location, size)
                if free_size[0] > blocks[0]:
                    self.free_slots.append(
                        (
                            (location[0] + blocks[0], location[1]),
                            (free_size[0] - blocks[0], free_size[1]),
                        )
                    )
                    if free_size[1] - blocks[1]:
                        self.free_slots.append(
                            (
                                (location[0], location[1] + blocks[1]),
                                (blocks[0], free_size[1] - blocks[1]),
                            )
                        )

                elif free_size[1] - blocks[1]:
                    self.free_slots.append(
                        (
                            (location[0], location[1] + blocks[1]),
                            (free_size[0], free_size[1] - blocks[1]),
                        )
                    )

                self.free_slots.sort(key=lambda x: x[1][0] * x[1][1])
                self.image.paste(
                    image,
                    (
                        location[0] * self.block_size[0],
                        (self.size[1] - location[1] - 1) * self.block_size[1],
                    ),
                )
                self._texture_cache = None
                return reference

        raise RuntimeError("no more space!")

    def get_texture(self) -> pyglet.image.AbstractImage:
        if self._texture_cache:
            return self._texture_cache

        self.image.save(config.TMP.joinpath("atlas.png"))
        self._texture_cache = pyglet.image.load(
            config.TMP.joinpath("atlas.png")
        ).get_texture()
        return self._texture_cache

    def refresh(self):
        self._texture_cache = None
