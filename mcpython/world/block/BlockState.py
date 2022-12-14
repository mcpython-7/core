import typing
from mcpython.world.block.Block import Block
from mcpython.backend.Registry import RegistryObject
import random


class BlockState:
    __slots__ = (
        "block_type",
        "chunk_section",
        "world_position",
        "block_state",
        "__previous_blockstate",
        "__blockstate_ref_cache",
        "nbt",
    )

    _RANDOM = random.Random()

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

    def __repr__(self):
        return f'BlockState("{self.block_type.NAME}"{self.world_position}, nbt={self.nbt}, state={self.block_state})'

    def with_state(self, state):
        self.block_state = state

        if self.chunk_section:
            self.chunk_section.update_block_visual(self)

        return self

    def get_positional_value(self, salt: typing.Hashable) -> float:
        """
        Returns a float value between 0 and 1 constant for the salt-position-dimension pair.
        Useful for e.g. block rendering
        """

        self._RANDOM.seed(
            hash(
                (
                    self.chunk_section.get_chunk().get_dimension().name,
                    self.world_position,
                    salt,
                )
            )
        )
        return self._RANDOM.random()

    def _check_blockstate_dirty(self) -> bool:
        return self.block_state == self.__previous_blockstate

    def _reset_dirty_blockstate(self):
        self.__previous_blockstate = self.block_state.copy()

    def _set_blockstate_ref_cache(self, cache: typing.Any):
        self.__blockstate_ref_cache = cache

    def _get_blockstate_ref_cache(self):
        return self.__blockstate_ref_cache

    async def on_addition(self, force=False, player=None) -> bool:
        return await self.block_type.on_added_to_world(self, force=force, player=player)

    async def on_remove(self, force=False, player=None) -> bool:
        return await self.block_type.on_removed_from_world(
            self, force=force, player=player
        )

    async def on_block_update(self, source=None):
        await self.block_type.on_block_update(self, source)

    async def on_random_update(self):
        await self.block_type.on_random_update()

    async def on_player_interaction(
        self, player, hand, button: int, modifiers: int, itemstack
    ) -> bool:
        return await self.block_type.on_player_interaction(
            self, player, hand, button, modifiers, itemstack
        )

    async def check_collision(
        self, position: typing.Tuple[float, float, float], source: object = None
    ) -> bool:
        return await self.block_type.check_collision(self, position, source)


Block.BLOCKSTATE_CLASS = BlockState
