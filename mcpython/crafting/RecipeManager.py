from __future__ import annotations

import typing

from mcpython.crafting.AbstractRecipe import AbstractRecipe, RecipeAttachmentException
from mcpython.resources.ResourceManager import ResourceManager

if typing.TYPE_CHECKING:
    from mcpython.crafting.GridRecipes import (
        GridShapedRecipe,
        GridShapelessRecipe,
    )


class RecipeManager:
    DECODERS: dict[str, type[AbstractRecipe]] = {}

    def __init__(self):
        self.shaped_recipes: dict[tuple[int, int], list[GridShapedRecipe]] = {}
        self.shapeless_recipes: dict[int, list[GridShapelessRecipe]] = {}

    def decode_recipe_file(self, file: str) -> AbstractRecipe:
        data = ResourceManager.load_json(file)

        decoder = self.DECODERS.get(data["type"])

        if decoder is None:
            raise InvalidRecipeType(f"unsupported recipe type: {data['type']}")

        return decoder.decode(data)

    def register_recipe_from_file(self, file: str) -> AbstractRecipe | None:
        try:
            recipe = self.decode_recipe_file(file)
        except InvalidRecipeType:
            return

        if recipe is None:
            return

        try:
            recipe.attach(self)
        except RecipeAttachmentException:
            print(f"Could not attach recipe loaded from {file}")
            return

        return recipe

    def load_providers(self):
        from mcpython.crafting.GridRecipes import GridShapelessRecipe, GridShapedRecipe

    def discover_recipes(self):
        for file in ResourceManager.list_directory(
            "data/minecraft/recipe", no_duplicates=False
        ):
            recipe = self.register_recipe_from_file(file)

            if recipe:
                recipe.attach(self)


RECIPE_MANAGER = RecipeManager()


class InvalidRecipeType(Exception):
    pass
