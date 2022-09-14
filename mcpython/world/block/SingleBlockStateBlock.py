import typing

from mcpython.world.block.Block import Block


class SingleBlockStateBlock(Block):
    def __init__(self, state: dict):
        super().__init__()
        self.state = state

    def get_all_valid_block_states(self) -> typing.List[dict]:
        return [self.state]

    async def on_added_to_world(self, blockstate, force=False, player=None) -> bool:
        blockstate.block_state = self.state
        return True

