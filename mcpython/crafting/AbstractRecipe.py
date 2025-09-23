from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from mcpython.crafting.RecipeManager import RecipeManager


class InvalidRecipeDataException(Exception):
    pass


class RecipeAttachmentException(Exception):
    pass


class AbstractRecipe:
    PROVIDER_NAME: str = None

    @classmethod
    def register(cls):
        assert cls.PROVIDER_NAME is not None

        from mcpython.crafting.RecipeManager import RECIPE_MANAGER

        RECIPE_MANAGER.DECODERS[cls.PROVIDER_NAME] = cls

    @classmethod
    def decode(cls, data: dict) -> AbstractRecipe | None:
        """
        Decodes the given recipe data into an instance of this recipe class

        WARNING: Returning an instance of another class (not subclass) is undefined behaviour

        :param data: the data to use
        :return: the recipe instance, or None if to silently ignore that recipe file
            (e.g. if your recipe file has conditions when it should be valid)
        :raises InvalidRecipeDataException: If the data in the recipe is broken
        """
        raise NotImplementedError

    def attach(self, manager: RecipeManager):
        """
        Attaches this recipe to the internal data structures associated with 'manager'

        :param manager: the manager to use
        :raises RecipeAttachmentException: if the recipe could not be attached (and that is fatal)
        """

    def detach(self, manager: RecipeManager):
        """
        Detaches this recipe from the given 'manager'

        :param manager: the manager to use
        :return: RecipeAttachmentException: if the recipe could not be detached.
            It is undefined behaviour to call detach() before a successful attach() call
        """
