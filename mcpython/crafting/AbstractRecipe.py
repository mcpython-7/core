from __future__ import annotations

from mcpython.crafting.GridRecipes import AbstractGridRecipe


class AbstractRecipe:
    PROVIDER_NAME: str = None

    @classmethod
    def decode(cls, data: dict) -> AbstractGridRecipe | None:
        raise NotImplementedError
