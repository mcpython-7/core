import abc

import pyglet.graphics.vertexdomain
from mcpython.rendering.TextureAtlas import TextureAtlas, AtlasReference


atlas = TextureAtlas()
dirt = atlas.add_image_from_path("minecraft:block/dirt")
stone = atlas.add_image_from_path("minecraft:block/stone")
sand = atlas.add_image_from_path("minecraft:block/sand")
bricks = atlas.add_image_from_path("minecraft:block/bricks")
bedrock = atlas.add_image_from_path("minecraft:block/bedrock")


def textured_cube(
    tex: AtlasReference, top: AtlasReference = None, bottom: AtlasReference = None
) -> list[float]:
    result = []
    base = tex.tex_coord()
    result.extend(top.tex_coord() if top else base)
    result.extend(bottom.tex_coord() if bottom else base)
    result.extend(base * 4)
    return result


# def tex_coords(
#     top: tuple[int, int], bottom: tuple[int, int], side: tuple[int, int], n=4
# ) -> list[float]:
#     """Return a list of the texture squares for the top, bottom and side."""
#     top = tex_coord(*top, n=n)
#     bottom = tex_coord(*bottom, n=n)
#     side = tex_coord(*side, n=n)
#     result = []
#     result.extend(top)
#     result.extend(bottom)
#     result.extend(side * 4)
#     return result


class AbstractBlock(abc.ABC):
    NAME: str | None = None
    TEXTURE_COORDINATES: list[float] | None = None
    BREAKABLE = True

    def __init__(self, position: tuple[int, int, int]):
        self.position = position
        self.shown = False
        self.vertex_data: pyglet.graphics.vertexdomain.VertexList | None = None

    def on_block_added(self):
        pass

    def on_block_removed(self):
        pass

    def on_block_updated(self):
        pass

    def on_block_interaction(self, button: int, modifiers: int) -> bool:
        """
        Called when the block is interacted with.
        'button' and 'modifiers' are the mouse buttons pressed.
        Should return 'True' if the normal logic should NOT continue.
        """
        return False

    def __repr__(self):
        return f"{self.__class__.__name__}{self.position}"


class Dirt(AbstractBlock):
    NAME = "minecraft:dirt"
    TEXTURE_COORDINATES = textured_cube(dirt)


class Sand(AbstractBlock):
    NAME = "minecraft:sand"
    TEXTURE_COORDINATES = textured_cube(sand)


class Bricks(AbstractBlock):
    NAME = "minecraft:bricks"
    TEXTURE_COORDINATES = textured_cube(bricks)


class Stone(AbstractBlock):
    NAME = "minecraft:stone"
    TEXTURE_COORDINATES = textured_cube(stone)


class Bedrock(AbstractBlock):
    NAME = "minecraft:bedrock"
    TEXTURE_COORDINATES = textured_cube(bedrock)
    BREAKABLE = False
