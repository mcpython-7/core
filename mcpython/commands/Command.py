from __future__ import annotations

import typing
from abc import ABC

if typing.TYPE_CHECKING:
    from mcpython.commands.Chat import Chat


INVALID = object()


class CommandElement(ABC):
    def __init__(self):
        self.possible_continue: list[CommandElement] = []
        self.run_action: (
            typing.Callable[[Chat, list[tuple[CommandElement, typing.Any]]], None]
            | None
        ) = None
        self.traverse_action: (
            typing.Callable[
                [
                    Chat,
                    list[tuple[CommandElement, typing.Any]],
                    CommandElement,
                    typing.Any,
                ],
                typing.Any,
            ]
            | None
        ) = None

    def then(self, element: CommandElement):
        self.possible_continue.append(element)
        return self

    def on_execute(
        self,
        action: typing.Callable[[Chat, list[tuple[CommandElement, typing.Any]]], None],
    ) -> typing.Callable[[Chat, list[tuple[CommandElement, typing.Any]]], None]:
        self.run_action = action
        return action

    def on_traverse(
        self,
        action: typing.Callable[
            [Chat, list[tuple[CommandElement, typing.Any]], CommandElement, typing.Any],
            typing.Any,
        ],
    ) -> typing.Callable[
        [Chat, list[tuple[CommandElement, typing.Any]], CommandElement, typing.Any],
        typing.Any,
    ]:
        self.traverse_action = action
        return action

    def parse_recursive(
        self,
        remaining_text: str,
        parsed_elements: list[tuple[CommandElement, typing.Any]],
    ) -> list[tuple[CommandElement, typing.Any]] | None:
        if (v := self.parse_partial(remaining_text, parsed_elements)) == INVALID:
            return

        text, value = v
        elements = parsed_elements + [(self, value)]

        if text == "":
            return elements

        for child in self.possible_continue:
            if tree := child.parse_recursive(text, elements):
                return tree

    def parse_partial(
        self,
        remaining_text: str,
        parsed_elements: list[tuple[CommandElement, typing.Any]],
    ) -> tuple[str, typing.Any] | object:
        raise NotImplementedError


class FixedString(CommandElement):
    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def parse_partial(
        self,
        remaining_text: str,
        parsed_elements: list[tuple[CommandElement, typing.Any]],
    ) -> tuple[str, typing.Any] | object:
        if remaining_text.startswith(f"{self.text} "):
            return remaining_text.removeprefix(f"{self.text} "), self.text

        return ("", self.text) if remaining_text == self.text else INVALID


class AnyString(CommandElement):
    def parse_partial(
        self,
        remaining_text: str,
        parsed_elements: list[tuple[CommandElement, typing.Any]],
    ) -> tuple[str, typing.Any] | object:
        element = remaining_text.split(" ")[0]
        return remaining_text.removeprefix(f"{element}").lstrip(), element


class ItemName(CommandElement):
    def parse_partial(
        self,
        remaining_text: str,
        parsed_elements: list[tuple[CommandElement, typing.Any]],
    ) -> tuple[str, typing.Any] | object:
        from mcpython.world.items.AbstractItem import ITEM_REGISTRY

        element = remaining_text.split(" ")[0]
        item = ITEM_REGISTRY.lookup(element)
        if item is None:
            return INVALID

        return remaining_text.removeprefix(f"{element}").lstrip(), item


class BlockName(CommandElement):
    def parse_partial(
        self,
        remaining_text: str,
        parsed_elements: list[tuple[CommandElement, typing.Any]],
    ) -> tuple[str, typing.Any] | object:
        from mcpython.world.blocks.AbstractBlock import BLOCK_REGISTRY

        element = remaining_text.split(" ")[0]
        item = BLOCK_REGISTRY.lookup(element)
        if item is None:
            return INVALID

        return remaining_text.removeprefix(f"{element}").lstrip(), item


COMMAND_REGISTRY: dict[str, Command] = {}


class Command:
    def __init__(self, base_name: str):
        self.base_name = base_name
        COMMAND_REGISTRY[base_name] = self
        self.base_node = FixedString(base_name)

    def construct(self) -> CommandElement:
        return self.base_node

    def try_parse(self, text: str) -> list[tuple[CommandElement, typing.Any]] | None:
        return self.base_node.parse_recursive(text, [])

    def run_command(self, chat: Chat, command: str):
        actions = self.try_parse(command)
        if actions is None or len(actions) == 0 or actions[-1][0].run_action is None:
            chat.submit_text("ERROR: invalid command")
            return

        for i, (node, value) in enumerate(actions):
            if node.traverse_action is not None:
                actions[i] = node, node.traverse_action(chat, actions[:i], node, value)

        actions[-1][0].run_action(chat, actions)


from mcpython.commands import GiveCommand
