from mcpython.backend.Registry import IRegistryEntry


class Block(IRegistryEntry):
    REGISTRY = "minecraft:block"

    def __init__(self):
        pass

    async def on_added_to_world(self, blockstate) -> bool:
        return True

    async def on_removed_from_world(self, blockstate, force=False, player=None) -> bool:
        return True

    async def on_block_update(self, blockstate, source=None):
        pass

    async def on_random_update(self):
        pass

    async def on_player_interaction(self, blockstate, player, hand, button, itemstack) -> bool:
        return False
