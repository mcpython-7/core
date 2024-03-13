from __future__ import annotations

import typing

from mcpython.resources.Registry import Registry
from mcpython.resources.ResourceManager import ResourceManager
from mcpython.world.blocks.AbstractBlock import BLOCK_REGISTRY
from mcpython.world.items.AbstractItem import ITEM_REGISTRY


class TagGroup:
    def __init__(self, group: str, bound_registry: Registry = None):
        self.group = group
        self.bound_registry = bound_registry
        self.tags: dict[str, list[str]] = {}

    def load_tag_by_name(self, name: str):
        return self.load_tag_file(
            f"data/{{}}/tags/{self.group}/{{}}.json".format(*name.split(":"))
        )

    def load_tag_file(self, file: str) -> list[str]:
        # data/<namespcae>/tags/<group>/<name>.json
        _, namespace, __, group, *name = file.split("/")
        full_name = f"{namespace}:{'/'.join(name).removesuffix('.json')}"

        if full_name in self.tags:
            return self.tags[full_name]
        self.tags[full_name] = tag_entries = []

        # todo: override tag files!
        data: dict[str, list[str]] = ResourceManager.load_json(file)
        for entry in data["values"]:
            if entry.startswith("#"):
                tag_entries.extend(self.load_tag_by_name(entry.removeprefix("#")))
            else:
                tag_entries.append(entry)

        if self.bound_registry:
            for entry in tag_entries:
                if item := self.bound_registry.lookup(entry):
                    item.TAGS.append(full_name)

        return tag_entries


TAG_ITEMS = TagGroup("items", ITEM_REGISTRY)
TAG_BLOCKS = TagGroup("blocks", BLOCK_REGISTRY)
