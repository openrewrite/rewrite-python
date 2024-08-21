from typing import Protocol, Any, ClassVar


class ExecutionContext(Protocol):
    REQUIRE_PRINT_EQUALS_INPUT: ClassVar[str] = "org.openrewrite.requirePrintEqualsInput"
    CHARSET: ClassVar[str] = "org.openrewrite.parser.charset"

    def get_message(self, key: str, default_value=None) -> Any:
        ...

    def put_message(self, key: str, value: Any):
        ...


class DelegatingExecutionContext(ExecutionContext):
    def __init__(self, delegate):
        self._delegate = delegate

    def get_message(self, key, default_value=None):
        return self._delegate.get_message(key, default_value)

    def put_message(self, key, value):
        self._delegate.put_message(key, value)


class InMemoryExecutionContext(ExecutionContext):
    _messages: dict[str, Any] = {}

    def get_message(self, key: str, default_value=None) -> Any:
        return self._messages[key] if key in self._messages else default_value

    def put_message(self, key: str, value: Any):
        self._messages[key] = value


class RecipeRunException(Exception):
    # FIXME implement
    pass


class Recipe:
    # FIXME implement
    pass
