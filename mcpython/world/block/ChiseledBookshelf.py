import typing

from mcpython.world.block.Block import Block


class ChiseledBookshelf(Block):
    def get_all_valid_block_states(self) -> typing.List[str]:
        return ['books_stored=0,facing=east', 'books_stored=0,facing=north', 'books_stored=0,facing=south',
                'books_stored=0,facing=west', 'books_stored=1,facing=east', 'books_stored=1,facing=north',
                'books_stored=1,facing=south', 'books_stored=1,facing=west', 'books_stored=2,facing=east',
                'books_stored=2,facing=north', 'books_stored=2,facing=south', 'books_stored=2,facing=west',
                'books_stored=3,facing=east', 'books_stored=3,facing=north', 'books_stored=3,facing=south',
                'books_stored=3,facing=west', 'books_stored=4,facing=east', 'books_stored=4,facing=north',
                'books_stored=4,facing=south', 'books_stored=4,facing=west', 'books_stored=5,facing=east',
                'books_stored=5,facing=north', 'books_stored=5,facing=south', 'books_stored=5,facing=west',
                'books_stored=6,facing=east', 'books_stored=6,facing=north', 'books_stored=6,facing=south',
                'books_stored=6,facing=west']
