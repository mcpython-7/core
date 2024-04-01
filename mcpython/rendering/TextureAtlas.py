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
        start: tuple[float, float],
        end: tuple[float, float],
    ):
        self.atlas = atlas
        self.start = start
        self.end = end

    def get_span_normalised(self) -> tuple[float, float, float, float]:
        mx, my = self.atlas.size
        bx, by = self.atlas.block_size
        x1, y1 = self.start
        x2, y2 = self.end
        x1 /= mx * bx
        y1 /= my * by
        x2 /= mx * bx
        y2 /= my * by
        return x1, y1, x2, y2

    def uv_section(self, uv: tuple[float, ...]) -> AtlasReference:
        if uv == (0, 0, 1, 1):
            return self

        if any(x < 0 or x > 1 for x in uv):
            raise ValueError("section must be in range [0; 1]!")

        a, b, c, d = uv
        x1, y1 = self.start
        x2, y2 = self.end

        return AtlasReference(
            self.atlas,
            (x1 + (x2 - x1) * a, y1 + (y2 - y1) * c),
            (x1 + (x2 - x1) * b, y1 + (y2 - y1) * d),
        )

    def tex_coord(self) -> tuple[float, ...]:
        """Return the bounding vertices of the texture square."""
        x1, y1, x2, y2 = self.get_span_normalised()
        # fmt: off
        return (
            x1, y1, x2, y1, x2, y2,  # Triangle 1
            x1, y1, x2, y2, x1, y2,  # Triangle 2
        )
        # fmt: on

    def get_texture(self) -> pyglet.image.AbstractImage:
        texture = self.atlas.get_texture()
        x1, y1 = self.start
        x2, y2 = self.end
        return texture.get_region(x1, y1, x2 - x1, y2 - y1)


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
                base = (
                    location[0] * self.block_size[0],
                    location[1] * self.block_size[1],
                )
                reference = AtlasReference(
                    self, base, (base[0] + size[0], base[1] + size[1])
                )
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
