import math
import os.path
import sys
import typing

import PIL.Image
import pyglet.image
import pyglet.gl as gl

MISSING_TEXTURE = PIL.Image.new("RGBA", (16, 16), (255, 0, 0, 255))


local = os.path.dirname(os.path.dirname(sys.argv[0]))


class TextureInfo:
    def __init__(self, atlas: "TextureAtlas", name: str, texture: PIL.Image.Image):
        self.atlas = atlas
        self.name = name
        self.texture = texture
        self.texture_quads = math.ceil(texture.width / 16), math.ceil(texture.height / 16)

        self.real_location = 0, 0

    def get_weight(self) -> int:
        return self.texture_quads[0] * self.texture_quads[1]

    def find_free(self, array: typing.List[typing.List[bool]]) -> typing.Tuple[int, int]:
        for x, row in enumerate(array[:-self.texture_quads[0]]):
            for y, cell in enumerate(row[:-self.texture_quads[1]]):
                if cell is True:
                    for dx in range(self.texture_quads[0]):
                        for dy in range(self.texture_quads[1]):
                            if not array[x+dx][y+dy]:
                                break
                        else:
                            continue
                        break
                    else:
                        for dx in range(self.texture_quads[0]):
                            for dy in range(self.texture_quads[1]):
                                array[x+dx][y+dy] = False
                        self.real_location = x, y
                        return x, y

        raise ValueError("No space found!")

    def prepare_tex_coords(self, coords: typing.List[int], part: int):
        step = 1 / self.atlas.size[0], 1 / self.atlas.size[1]

        for i, e in enumerate(coords[part * 12 : part * 12 + 12]):
            pos = self.real_location[i % 2]

            coords[part * 12 + i] = (pos + e) * step[i % 2]


class TextureAtlas:
    def __init__(self, initial_size=(16, 16)):
        self.size = initial_size
        self.texture = PIL.Image.new("RGBA", (initial_size[0] * 16, initial_size[1] * 16), (255, 255, 255, 255))
        self.pyglet_image = None
        self.pyglet_texture = None

        self.textures: typing.Dict[str, TextureInfo] = {}

    def add_texture(self, name: str, texture: PIL.Image.Image) -> TextureInfo:
        if name in self.textures: return self.textures[name]

        info = TextureInfo(self, name, texture)
        self.textures[name] = info
        return info

    def bake(self):
        # Sort them reversed and filter out missing texture
        textures = list(filter(lambda e: e.name != "MISSING_TEXTURE", list(sorted(self.textures.values(), key=TextureInfo.get_weight, reverse=True))))

        missing = self.textures["MISSING_TEXTURE"] = TextureInfo(self, "MISSING_TEXTURE", MISSING_TEXTURE)
        free_cells = [[True] * self.size[1]] * self.size[0]
        if missing.find_free(free_cells) != (0, 0):
            raise RuntimeError("something went horribly wrong :-(")

        for texture in textures:
            if texture.find_free(free_cells) is None:
                raise RuntimeError(f"Could not allocate space for texture {texture.name}")

        for texture in self.textures.values():
            self.texture.paste(texture.texture, (texture.real_location[0] * 16, (self.size[1] - texture.real_location[1] - 1) * 16))

        self.texture.save(local+"/cache/atlas.png")

        self.pyglet_image = pyglet.image.load(local+"/cache/atlas.png")
        self.pyglet_texture = self.pyglet_image.get_texture()
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)


