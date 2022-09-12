import typing
from mcpython.world.block.Block import Block
from mcpython.backend.Registry import RegistryObject


class BlockState:
    def __init__(self, block_type: Block | RegistryObject = None):
        self.block_type = (
            block_type
            if not isinstance(block_type, RegistryObject)
            else block_type.get()
        )

        # The Section instance this block is in
        self.chunk_section = None
        self.world_position: typing.Tuple[int, int, int] = None

        self.block_state: typing.Dict[str, str] = {}
        self.__previous_blockstate = {}
        self.__blockstate_ref_cache = None
        self.nbt: typing.Dict[str, object] = {}

    def _check_blockstate_dirty(self) -> bool:
        return self.block_state == self.__previous_blockstate

    def _reset_dirty_blockstate(self):
        self.__previous_blockstate = self.block_state.copy()

    def _set_blockstate_ref_cache(self, cache: typing.Any):
        self.__blockstate_ref_cache = cache

    def _get_blockstate_ref_cache(self):
        return self.__blockstate_ref_cache

    async def on_addition(self) -> bool:
        return await self.block_type.on_added_to_world(self)

    async def on_remove(self, force=False, player=None) -> bool:
        return await self.block_type.on_removed_from_world(self, force, player)

    async def on_block_update(self, source=None):
        await self.block_type.on_block_update(self, source)

    async def on_random_update(self):
        await self.block_type.on_random_update()

    async def on_player_interaction(
        self, blockstate, player, hand, button, itemstack
    ) -> bool:
        return await self.block_type.on_player_interaction(
            blockstate, player, hand, button, itemstack
        )
