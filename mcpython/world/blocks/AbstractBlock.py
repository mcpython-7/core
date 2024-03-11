from __future__ import annotations

import abc
import typing

import pyglet.graphics.vertexdomain

from mcpython.rendering.Models import BlockStateFile

if typing.TYPE_CHECKING:
    from mcpython.containers.ItemStack import ItemStack


_EMPTY_STATE = {}


class AbstractBlock(abc.ABC):
    NAME: str | None = None
    STATE_FILE: BlockStateFile | None = None
    BREAKABLE = True

    def __init__(self, position: tuple[int, int, int]):
        self.position = position
        self.shown = False
        self.vertex_data: pyglet.graphics.vertexdomain.VertexList | None = None

    def set_block_state(self, state: dict[str, str]):
        pass

    def get_block_state(self) -> dict[str, str]:
        return _EMPTY_STATE

    def on_block_added(self):
        pass

    def on_block_removed(self):
        pass

    def on_block_updated(self):
        pass

    def on_block_interaction(
        self, itemstack: ItemStack, button: int, modifiers: int
    ) -> bool:
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
    STATE_FILE = BlockStateFile.by_name(NAME)


class Sand(AbstractBlock):
    NAME = "minecraft:sand"
    STATE_FILE = BlockStateFile.by_name(NAME)

    def __init__(self, position):
        super().__init__(position)
        self.falling = False

    def on_block_updated(self):
        from mcpython.world.World import World

        if (
            self.position[0],
            self.position[1] - 1,
            self.position[2],
        ) not in World.INSTANCE.world:
            pyglet.clock.schedule_once(self.fall, 0.5)
            self.falling = True

    def fall(self, _):
        from mcpython.world.World import World

        self.falling = False

        if (
            World.INSTANCE.world.get(self.position, None) is self
            and (
                self.position[0],
                self.position[1] - 1,
                self.position[2],
            )
            not in World.INSTANCE.world
        ):
            World.INSTANCE.remove_block(self.position, block_update=False)
            old_pos = self.position
            World.INSTANCE.add_block(
                (self.position[0], self.position[1] - 1, self.position[2]), self
            )
            World.INSTANCE.send_block_update(old_pos)


class Bricks(AbstractBlock):
    NAME = "minecraft:bricks"
    STATE_FILE = BlockStateFile.by_name(NAME)


class Stone(AbstractBlock):
    NAME = "minecraft:stone"
    STATE_FILE = BlockStateFile.by_name(NAME)


class OakPlanks(AbstractBlock):
    NAME = "minecraft:oak_planks"
    STATE_FILE = BlockStateFile.by_name(NAME)


class Bedrock(AbstractBlock):
    NAME = "minecraft:bedrock"
    STATE_FILE = BlockStateFile.by_name(NAME)
    BREAKABLE = False


BlockStateFile.bake_all()
