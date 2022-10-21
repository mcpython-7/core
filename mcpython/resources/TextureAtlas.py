import math
import os.path
import sys
import typing

import PIL.Image
import pyglet.image
import pyglet.gl as gl

MISSING_TEXTURE = PIL.Image.new("RGBA", (16, 16), (255, 0, 0, 255))


local = os.path.dirname(os.path.dirname(sys.argv[0]))


# fmt: off
UV_PART_ORDER = [
    (1, 0), (1, 1), (0, 1),
    (1, 0), (0, 1), (0, 0),
]
# fmt: on


class TextureInfo:
    def __init__(self, atlas: "TextureAtlas", name: str, texture: PIL.Image.Image):
        self.atlas = atlas
        self.name = name
        self.texture = texture
        self.texture_quads = math.ceil(texture.width / 16), math.ceil(
            texture.height / 16
        )

        self.real_location = 0, 0

    def get_weight(self) -> int:
        return self.texture_quads[0] * self.texture_quads[1]

    def find_free(
        self, array: typing.List[typing.List[bool]]
    ) -> typing.Tuple[int, int]:
        for x, row in enumerate(array[: -self.texture_quads[0]]):
            for y, cell in enumerate(row[: -self.texture_quads[1]]):
                if cell is True:
                    for dx in range(self.texture_quads[0]):
                        for dy in range(self.texture_quads[1]):
                            if not array[x + dx][y + dy]:
                                break
                        else:
                            continue
                        break
                    else:
                        for dx in range(self.texture_quads[0]):
                            for dy in range(self.texture_quads[1]):
                                array[x + dx][y + dy] = False
                        self.real_location = x, y
                        return x, y

    def prepare_tex_coords(self, coords: typing.List[int], part: int, uv=(0, 0, 1, 1)):
        step = 1 / self.atlas.size[0], 1 / self.atlas.size[1]

        coord_section = coords[part * 12 : part * 12 + 12]

        for i, e in enumerate(coord_section):
            # What x/y offset on the texture is used?
            pos = self.real_location[i % 2]

            # Look up on what part of the face we are, either lower side (0) or upper side (1)
            uv_entry = UV_PART_ORDER[i // 2][i % 2]

            # Look up the uv coord based on the side and x or y
            uv_part = uv[uv_entry * 2 + (i % 2)]

            # What offset this corresponds to, - uv_entry such that a uv of 1 at upper side corresponds to an offset of 0
            offset = (uv_part - uv_entry)

            # Don't really know why this invert is needed, but seems like UV_PART_ORDER is slightly wrong in some cases
            if (e == 0 and offset < 0) or (e == 1 and offset > 0):
                offset = -offset

            # Now insert the new uv into the array, by using the texture position, the texture coord info, and the offset by the uv multiplied by the inverse of the texture atlas size
            coords[part * 12 + i] = (pos + e + offset) * step[i % 2]


class TextureAtlas:
    def __init__(self, initial_size=(16, 16)):
        self.size = initial_size
        self.texture = PIL.Image.new(
            "RGBA", (initial_size[0] * 16, initial_size[1] * 16), (255, 255, 255, 255)
        )
        self.pyglet_image = None
        self.pyglet_texture = None

        self.textures: typing.Dict[str, TextureInfo] = {
            "MISSING_TEXTURE": TextureInfo(self, "MISSING_TEXTURE", MISSING_TEXTURE)
        }

    def add_texture(self, name: str | None, texture: PIL.Image.Image) -> TextureInfo:
        if name is None:
            return self.textures["MISSING_TEXTURE"]

        if name in self.textures:
            return self.textures[name]

        info = TextureInfo(self, name, texture)
        self.textures[name] = info
        return info

    def bake(self):
        # Sort them reversed and filter out missing texture
        textures = list(
            filter(
                lambda e: e.name != "MISSING_TEXTURE",
                list(
                    sorted(
                        self.textures.values(), key=TextureInfo.get_weight, reverse=True
                    )
                ),
            )
        )

        missing = self.textures["MISSING_TEXTURE"]
        free_cells = [[True] * self.size[1] for _ in range(self.size[0])]
        if missing.find_free(free_cells) != (0, 0):
            raise RuntimeError("something went horribly wrong :-(")

        for texture in textures:
            while texture.find_free(free_cells) is None:
                x, y = self.size
                self.size = (self.size[0] * 2, self.size[1] * 2)
                self.texture = PIL.Image.new(
                    "RGBA", (self.size[0] * 16, self.size[1] * 16), (255, 255, 255, 255)
                )
                free_cells = [e + [True] * y for e in free_cells]
                free_cells += [[True] * self.size[1] for _ in range(x)]
                print("increased size to", self.size)

        for texture in self.textures.values():
            self.texture.paste(
                texture.texture,
                (
                    texture.real_location[0] * 16,
                    (self.size[1] - texture.real_location[1] - 1) * 16,
                ),
            )

        self.texture.save(local + "/cache/atlas.png")

        self.pyglet_image = pyglet.image.load(local + "/cache/atlas.png")
        self.pyglet_texture = self.pyglet_image.get_texture()
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
