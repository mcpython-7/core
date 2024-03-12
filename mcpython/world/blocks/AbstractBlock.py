from __future__ import annotations

import abc
import enum
import typing

import pyglet.graphics.vertexdomain

from mcpython.rendering.Models import BlockStateFile

if typing.TYPE_CHECKING:
    from mcpython.world.items.AbstractItem import AbstractItem
    from mcpython.containers.ItemStack import ItemStack


_EMPTY_STATE = {}


class AbstractBlock(abc.ABC):
    NAME: str | None = None
    STATE_FILE: BlockStateFile | None = None
    BREAKABLE = True
    BLOCK_ITEM: type[AbstractItem] | None = None

    def __init__(self, position: tuple[int, int, int]):
        self.position = position
        self.shown = False
        self.vertex_data: pyglet.graphics.vertexdomain.VertexList | None = None

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


class LogAxis(enum.Enum):
    X = 0
    Y = 1
    Z = 2


class OakLog(AbstractBlock):
    NAME = "minecraft:oak_log"
    STATE_FILE = BlockStateFile.by_name(NAME)

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


class Bedrock(AbstractBlock):
    NAME = "minecraft:bedrock"
    STATE_FILE = BlockStateFile.by_name(NAME)
    BREAKABLE = False


BlockStateFile.bake_all()
