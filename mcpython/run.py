from __future__ import annotations

import pyglet.graphics.shader
from pyglet.gl import *
import pyglet.model.codecs.obj

from mcpython.containers.ItemStack import ItemStack
from mcpython.crafting.GridRecipes import RECIPE_MANAGER
from mcpython.rendering.Models import BlockStateFile
from mcpython.world.World import World

pyglet.image.Texture.default_min_filter = GL_NEAREST
pyglet.image.Texture.default_mag_filter = GL_NEAREST

from mcpython.rendering.Window import Window
from mcpython.rendering.util import (
    setup_fog,
)

from mcpython.world.blocks.AbstractBlock import BLOCK_REGISTRY
from mcpython.world.items.AbstractItem import ITEM_REGISTRY

pyglet.resource.path.append("../cache/assets.zip")


def setup():
    """Basic OpenGL configuration."""
    # Set the color of "clear", i.e. the sky, in rgba.
    glClearColor(0.5, 0.69, 1.0, 1)
    # Enable culling (not rendering) of back-facing facets -- facets that aren't
    # visible to you.
    glEnable(GL_CULL_FACE)
    # Set the texture minification/magnification function to GL_NEAREST (nearest
    # in Manhattan distance) to the specified texture coordinates. GL_NEAREST
    # "is generally faster than GL_LINEAR, but it can produce textured images
    # with sharper edges because the transition between texture elements is not
    # as smooth."
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    setup_fog()


def main():
    ITEM_REGISTRY.run_registrations()
    BLOCK_REGISTRY.run_registrations()

    BlockStateFile.bake_all()

    window = Window(width=800, height=600, caption="mcpython 7", resizable=True)
    # Hide the mouse cursor and prevent the mouse from leaving the window.
    window.set_exclusive_mouse(True)
    setup()

    RECIPE_MANAGER.discover_recipes()

    pyglet.app.run()


if __name__ == "__main__":
    main()
