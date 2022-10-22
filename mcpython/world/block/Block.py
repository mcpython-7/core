import typing

from mcpython.backend.Registry import IRegistryEntry, RegistryObject
from mcpython.util.math import normalize


class BlockUtil:
    @classmethod
    async def update_visual(cls, blockstate):
        await blockstate.chunk_section.update_block_visual(blockstate)


class Block(IRegistryEntry):
    REGISTRY = "minecraft:block"
    BLOCKSTATE_CLASS = None  # Reference to a BlockState-like class
    BLOCK_ITEM_INSTANCE: RegistryObject = None
    BLOCK_RENDERER = None

    def __init__(self):
        pass

    def set_breakable(self, flag: bool):
        return self

    def get_all_valid_block_states(self) -> typing.List[dict | str]:
        return [{}]

    async def on_register(self):
        from mcpython.client.rendering.BlockRendering import BlockRenderer, MANAGER

        self.BLOCK_RENDERER = BlockRenderer(self.NAME)
        MANAGER.renderers.append(self.BLOCK_RENDERER)

    def register_block_item(self):
        from mcpython.world.item.BlockItem import BlockItem
        from mcpython.world.item.ItemManager import ITEM_REGISTRY

        self.BLOCK_ITEM_INSTANCE = ITEM_REGISTRY.register_lazy(
            self.NAME,
            lambda: BlockItem().set_registry_name(self.NAME).set_block_type(self),
        )
        return self

    def get_blockstate_class(self):
        return self.BLOCKSTATE_CLASS

    async def on_added_to_world(self, blockstate, force=False, player=None) -> bool:
        """
        Invoked when the block is added to the world.
        on_block_update() is invoked afterwards (when the adding instance ask for block updates).
        Should be invoked before any of the other functions are invoked, when not stated otherwise.
        Invoked on the same thread as the adding block call is using

        :param blockstate: the respective block state
        :param force: if the block is force-added to the world
        :param player: the player instance adding the block
        :return: if to add the block or not
        """
        return True

    async def on_removed_from_world(self, blockstate, force=False, player=None) -> bool:
        """
        Invoked when the block is removed from the world

        :param blockstate: the blockstate representing the block
        :param force: if force-removal is scheduled
        :param player: the player breaking, if provided
        :return: True to break the block, False if not, if force is True, this is ignored
        """
        return True

    async def on_starting_to_break(
        self, blockstate, itemstack, force=False, player=None
    ):
        """
        Similar to on_removed_from_world(), but is invoked before the break animation starts,
        so you can early cancel the breaking
        """
        return True

    async def on_block_update(self, blockstate, source=None):
        """
        Invoked when a block-update hits this block
        May be executed in a processing thread, so do not directly interact with critical systems
        'source' is the source of the update, varying based on context.
        Could be Player, block position, blockstate, ...
        """

    async def on_random_update(self):
        """
        Invoked when a random update hits this block
        May be executed in a processing thread, so do not directly interact with critical systems
        """

    async def on_player_interaction(
        self, blockstate, player, hand, button, modifiers, itemstack
    ) -> bool:
        """
        Method invoked when the block is interacted with by the player.
        Block breaking and adding is handled afterwards by default!

        :param blockstate: the block state of the block
        :param player: the player instance
        :param hand: the hand, as an enum value
        :param button: the mouse button, see pyglet.window.mouse
        :param modifiers: what modifiers are used
        :param itemstack: the itemstack used
        :return: True if the event is handled, False otherwise
        """
        return False

    async def check_collision(
        self,
        blockstate,
        position: typing.Tuple[float, float, float],
        source: object = None,
    ) -> bool:
        return normalize(*position) == blockstate.world_position
