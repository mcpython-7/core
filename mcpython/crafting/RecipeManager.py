from __future__ import annotations

from mcpython.crafting.GridRecipes import (
    GridShapedRecipe,
    GridShapelessRecipe,
    AbstractGridRecipe,
    InvalidRecipeType,
)
from mcpython.resources.ResourceManager import ResourceManager


class RecipeManager:
    DECODERS = [
        GridShapedRecipe,
        GridShapelessRecipe,
    ]

    def __init__(self):
        self.shapeless_recipes: dict[int, list[GridShapelessRecipe]] = {}
        self.shaped_recipes: dict[tuple[int, int], list[GridShapedRecipe]] = {}

    def decode_recipe_file(self, file: str) -> AbstractGridRecipe:
        data = ResourceManager.load_json(file)

        for decoder in self.DECODERS:
            if data["type"] == decoder.PROVIDER_NAME:
                return decoder.decode(data)

        raise InvalidRecipeType(f"unsupported recipe type: {data['type']}")

    def register_recipe_from_file(self, file: str) -> AbstractGridRecipe | None:
        try:
            recipe = self.decode_recipe_file(file)
        except InvalidRecipeType:
            return

        if recipe is None:
            return

        if isinstance(recipe, GridShapedRecipe):
            self.shaped_recipes.setdefault(recipe.size, []).append(recipe)
        elif isinstance(recipe, GridShapelessRecipe):
            self.shapeless_recipes.setdefault(len(recipe.itemlist), []).append(recipe)
        else:
            raise InvalidRecipeType(f"unsupported recipe to register: {recipe}")

        return recipe

    def discover_recipes(self):
        from mcpython.rendering.Window import Window

        for file in ResourceManager.list_directory(
            "data/minecraft/recipes", no_duplicates=False
        ):
            recipe = self.register_recipe_from_file(file)
            if file == "data/minecraft/recipes/oak_wood.json":
                recipe: GridShapelessRecipe


RECIPE_MANAGER = RecipeManager()
