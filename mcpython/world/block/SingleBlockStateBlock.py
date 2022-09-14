from mcpython.world.block.Block import Block


class SingleBlockStateBlock(Block):
    def __init__(self, state: dict):
        super().__init__()
        self.state = state

    async def on_added_to_world(self, blockstate, force=False, player=None) -> bool:
        blockstate.block_state = self.state
        return True

