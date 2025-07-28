from __future__ import annotations

import typing

from mcpython.containers.AbstractContainer import Slot, Container
from mcpython.containers.ItemStack import ItemStack, TagStack
from mcpython.resources.ResourceManager import ResourceManager


def _normalize(
    items: tuple[tuple[ItemStack | None, ...], ...],
) -> tuple[tuple[ItemStack | None, ...], ...]:
    lrn = lcn = 0
    frn = len(items[0])
    fcn = len(items)

    for c, col in enumerate(items):
        for r, item in enumerate(col):
            if item is not None:
                frn = min(frn, r)
                lrn = max(lrn, r)
                fcn = min(fcn, c)
                lcn = max(lcn, c)

    return tuple(col[frn : lrn + 1] for col in items[fcn : lcn + 1])


def _normalize_slots(
    items: tuple[tuple[Slot, ...], ...],
) -> tuple[tuple[Slot, ...], ...]:
    lrn = lcn = 0
    frn = len(items[0])
    fcn = len(items)

    for c, col in enumerate(items):
        for r, slot in enumerate(col):
            if not slot.itemstack.is_empty():
                frn = min(frn, r)
                lrn = max(lrn, r)
                fcn = min(fcn, c)
                lcn = max(lcn, c)

    return tuple(col[frn : lrn + 1] for col in items[fcn : lcn + 1])


def _decode_ingredient(entry: dict | list) -> ItemStack:
    if isinstance(entry, list):
        return TagStack(None, [_decode_ingredient(entry) for entry in entry])

    if "tag" in entry:
        return TagStack(entry["tag"])

    return ItemStack(
        entry["item"],
        entry.get("count", 1),
    )


class AbstractGridRecipe:
    PROVIDER_NAME: str = None

    @classmethod
    def decode(cls, data: dict) -> AbstractGridRecipe | None:
        raise NotImplementedError

    def matches(self, itemlist) -> ItemStack | None:
        """
        Matches the given itemlist (depending on the type of recipe) and returns
        the output stack or None
        """
        raise NotImplementedError

    def remove(self, slotlist):
        """
        Removes the required item amount from the slotlist, in the same format as the itemlist in matches()
        Should NOT invoke the on_update on the slots (Slot.set_stack(<value>, update=False)!
        """
        raise NotImplementedError


class GridShapedRecipe(AbstractGridRecipe):
    PROVIDER_NAME = "minecraft:crafting_shaped"

    @classmethod
    def decode(cls, data: dict) -> GridShapedRecipe | None:
        table = {" ": ItemStack.EMPTY} | {
            key: _decode_ingredient(value) for key, value in data["key"].items()
        }
        if any(value.is_empty() for key, value in table.items() if key != " "):
            return

        pattern = data["pattern"]
        size = len(pattern[0]), len(pattern)
        table = tuple(
            tuple(table[pattern[y][x]] for y in range(size[1])) for x in range(size[0])
        )
        output = _decode_ingredient(data["result"])
        if output.is_empty():
            return

        return cls(table, output)

    def __init__(
        self, itemlist: tuple[tuple[ItemStack | None, ...], ...], output: ItemStack
    ):
        self.itemlist = itemlist
        self.output = output
        self.size = len(itemlist), len(itemlist[0])

    def matches(
        self, item_grid: tuple[tuple[ItemStack | None, ...], ...]
    ) -> ItemStack | None:
        for a, b in zip(item_grid, self.itemlist):
            for x, y in zip(a, b):
                if x is None and not y.is_empty():
                    return
                elif not x.is_compatible(y) or x.count < y.count:
                    return

        return self.output

    def remove(self, slotlist):
        for a, b in zip(slotlist, self.itemlist):
            for x, y in zip(a, b):
                x.set_stack(x.itemstack.add_amount(-y.count), update=False)


class GridShapelessRecipe(AbstractGridRecipe):
    PROVIDER_NAME = "minecraft:crafting_shapeless"

    @classmethod
    def decode(cls, data: dict) -> GridShapelessRecipe | None:
        items = [_decode_ingredient(entry) for entry in data["ingredients"]]
        if any(entry.is_empty() for entry in items):
            return
        output = _decode_ingredient(data["result"])
        if output.is_empty():
            return
        return cls(items, output)

    def __init__(self, itemlist: list[ItemStack], output: ItemStack):
        self.itemlist = itemlist
        self.output = output

    def matches(self, item_grid: list[ItemStack]) -> ItemStack | None:
        pending = self.itemlist.copy()
        for item in item_grid:
            for p in pending:
                if item.is_compatible(p) and p.count <= item.count:
                    break
            else:
                return
            pending.remove(p)
        return self.output

    def remove(self, slotlist):
        pending = self.itemlist.copy()
        for slot in slotlist:
            for p in pending:
                if slot.itemstack.is_compatible(p) and p.count <= slot.itemstack.count:
                    break
            else:
                raise RuntimeError()

            pending.remove(p)
            slot.set_stack(slot.itemstack.add_amount(-p.count), update=False)


class InvalidRecipeType(Exception):
    pass


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


class GridRecipeManager:
    def __init__(
        self,
        back_container: Container,
        size: tuple[int, int],
        slots: tuple[tuple[Slot, ...], ...],
        output: Slot,
    ):
        if len(slots) != size[0] or len(slots[0]) != size[1]:
            raise ValueError("dimensions must match!")

        self.size = size
        self.slots = slots
        self.output = output
        self.current_recipe: AbstractGridRecipe | None = None
        self.current_output: ItemStack | None = None
        self.normalised_slots = None

        # todo: what do we do when there's already a function?
        for col in slots:
            for slot in col:
                slot.on_update = self.input_update
        output.on_update = self.output_update

    def get_item_grid(self) -> tuple[tuple[ItemStack | None, ...], ...]:
        return tuple(
            tuple(None if slot.itemstack.is_empty() else slot.itemstack for slot in col)
            for col in self.slots
        )

    def get_matching_recipe(
        self, grid: tuple[tuple[ItemStack | None, ...], ...] = None
    ) -> tuple[AbstractGridRecipe, ItemStack, typing.Any] | tuple[None, None, None]:
        grid = grid or _normalize(self.get_item_grid())
        if not grid:
            return None, None, None
        size = len(grid), len(grid[0])

        if size in RECIPE_MANAGER.shaped_recipes:
            for recipe in RECIPE_MANAGER.shaped_recipes[size]:
                if item := recipe.matches(grid):
                    return recipe, item, _normalize_slots(self.slots)

        flattened = sum(map(list, _normalize_slots(self.slots)), [])
        i = 0
        while i < len(flattened):
            if flattened[i] is None:
                del flattened[i]
            else:
                i += 1

        if len(flattened) in RECIPE_MANAGER.shapeless_recipes:
            items = [slot.itemstack for slot in flattened]
            for recipe in RECIPE_MANAGER.shapeless_recipes[len(flattened)]:
                if item := recipe.matches(items):
                    return recipe, item, flattened

        return None, None, None

    def input_update(self, slot, old):
        recipe, item, slots = self.get_matching_recipe()
        if recipe == self.current_recipe and item == self.current_output:
            return

        self.current_recipe = recipe
        self.current_output = item
        self.output.set_stack(item, update=False)
        self.normalised_slots = slots

    def output_update(self, slot, old):
        if slot.itemstack.is_empty() and self.current_output is not None:
            self.current_recipe.remove(self.normalised_slots)

            recipe, item, slots = self.get_matching_recipe()
            if recipe == self.current_recipe and item == self.current_output:
                slot.set_stack(item, update=False)
                return

            recipe, item, slots = self.get_matching_recipe()
            if recipe == self.current_recipe and item == self.current_output:
                return

            self.current_recipe = recipe
            self.current_output = item
            self.output.set_stack(item, update=False)
            self.normalised_slots = slots
