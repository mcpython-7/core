import typing

from mcpython.backend.EventHandler import EventHandler


class Mod:
    def __init__(self, name: str, version: typing.Tuple[int, ...]):
        self.name = name
        self.version = version

        self.event_handler = EventHandler(f"mod event handler for {name}")
        self.event_handler.register_event_type("mod-loading:dependency_scan_success")
        self.event_handler.register_event_type("mod-loading:dependency_scan_failed")
        self.event_handler.register_event_type("mod-loading:dependency_scan_failed:total")
        self.event_handler.register_event_type("mod-loading:load_if_success")
        self.event_handler.register_event_type("mod-loading:load_if_failed")
        self.event_handler.register_event_type("mod-loading:load_if_failed:total")

        self.event_handler.register_event_type("mod-loading:all_dependency_checks_success")

        self.event_handler.register_event_type("mod-loading:mod-loading-order-set")

        self.event_handler.register_event_type("mod-loading:prepare-mod")

        self.enabled = True

    def add_dependency(self, name: str, version_checker: typing.Callable[[typing.Tuple[int, ...]], bool] = lambda _: True):
        pass

    def add_incompatible(self, name: str, version_checker: typing.Callable[[typing.Tuple[int, ...]], bool] = lambda _: True):
        pass

    def add_load_if_dependency(self, name: str, version_checker: typing.Callable[[typing.Tuple[int, ...]], bool] = lambda _: True):
        pass

    def add_load_if_not_present_dependency(self, name: str, version_checker: typing.Callable[[typing.Tuple[int, ...]], bool] = lambda _: True):
        pass

    def get_mod_order_dependencies(self) -> typing.List[str]:
        return []

    def check_dependency_graph(self) -> bool:
        pass
