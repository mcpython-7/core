from __future__ import annotations

import abc
import enum
import typing

import pyglet.graphics.vertexdomain

from mcpython.rendering.Models import BlockStateFile
from mcpython.resources.Registry import IRegisterAble, Registry

if typing.TYPE_CHECKING:
    from mcpython.world.items.AbstractItem import AbstractItem
    from mcpython.containers.ItemStack import ItemStack


_EMPTY_STATE = {}


class AbstractBlock(IRegisterAble, abc.ABC):
    NAME: str | None = None
    STATE_FILE: BlockStateFile | None = None
    BREAKABLE = True

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.NAME is not None and cls.STATE_FILE is None:
            cls.STATE_FILE = BlockStateFile.by_name(cls.NAME)

    def __init__(self, position: tuple[int, int, int]):
        self.position = position
        self.shown = False
        self.vertex_data: list[pyglet.graphics.vertexdomain.VertexList] = []

    def set_block_state(self, state: dict[str, str]):
        pass

    def get_block_state(self) -> dict[str, str]:
        return _EMPTY_STATE

    def update_render_state(self):
        if not self.shown:
            return

        from mcpython.rendering.Window import Window

        world = Window.INSTANCE.world
        world.hide_block(self)
        world.show_block(self)

    def on_block_added(self):
        pass

    def on_block_placed(self, itemstack: ItemStack, onto: tuple[int, int, int]):
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


BLOCK_REGISTRY = Registry("minecraft:block", AbstractBlock)


@BLOCK_REGISTRY.register
class Dirt(AbstractBlock):
    NAME = "minecraft:dirt"
    STATE_FILE = BlockStateFile.by_name(NAME)


@BLOCK_REGISTRY.register
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


@BLOCK_REGISTRY.register
class Bricks(AbstractBlock):
    NAME = "minecraft:bricks"
    STATE_FILE = BlockStateFile.by_name(NAME)


@BLOCK_REGISTRY.register
class Stone(AbstractBlock):
    NAME = "minecraft:stone"
    STATE_FILE = BlockStateFile.by_name(NAME)


class LogAxis(enum.Enum):
    X = 0
    Y = 1
    Z = 2


class LogLikeBlock(AbstractBlock):
    def __init__(self, position: tuple[int, int, int]):
        super().__init__(position)
        self.axis = LogAxis.Y

    def on_block_placed(self, itemstack: ItemStack, onto: tuple[int, int, int]):
        dx, dy, dz = (
            self.position[0] - onto[0],
            self.position[1] - onto[1],
            self.position[2] - onto[2],
        )
        print(dx, dy, dz)

        if dy != 0:
            self.axis = LogAxis.Y
        elif dx != 0:
            self.axis = LogAxis.X
        elif dz != 0:
            self.axis = LogAxis.Z
        else:
            self.axis = LogAxis.Y

        self.update_render_state()

    def get_block_state(self) -> dict[str, str]:
        return {"axis": self.axis.name.lower()}

    def set_block_state(self, block_state: dict[str]):
        self.axis = LogAxis[block_state.get("axis", "y").upper()]


@BLOCK_REGISTRY.register
class Bedrock(AbstractBlock):
    NAME = "minecraft:bedrock"
    BREAKABLE = False
