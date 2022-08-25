import typing


class BlockState:
    def __init__(self):
        self.block_type = None
        self.section = None
        self.position: typing.Tuple[int, int, int] = None

    async def on_addition(self):
        pass

    async def on_remove(self, force=False, player=None) -> bool:
        pass
