import os.path
import sys

import pyglet
import PIL.Image
from pyglet.graphics.shader import Shader
from pyglet.graphics.shader import ShaderProgram
from pyglet.model import Model
from pyglet.resource import FileLocation

from mcpython.resources.ResourceManagement import MANAGER as RESOURCE_MANAGER


local = os.path.dirname(os.path.dirname(sys.argv[0]))


class BlockRenderer:
    TEXTURE = None
    TEXTURE_GROUP = None
    SHADER = None

    async def add_to_batch(self, batch: pyglet.graphics.Batch):
        pyglet.resource._default_loader.reindex()
        pyglet.resource._default_loader._index["box.obj"] = FileLocation(
            local + "/mcpython/client/rendering"
        )
        pyglet.resource._default_loader._index["box.mtl"] = FileLocation(
            local + "/mcpython/client/rendering"
        )
        pyglet.resource._default_loader._index["pyglet.png"] = FileLocation(
            local + "/mcpython/client/rendering"
        )
        self.model_box: Model = pyglet.resource.model("box.obj", batch=batch)
        self.model_box.matrix.from_translation((0, 0, 0))
