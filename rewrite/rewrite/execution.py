from typing import Protocol, Any, ClassVar, TYPE_CHECKING

if TYPE_CHECKING:
    from .visitor import TreeVisitor


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
    def __init__(self, cause: Exception, cursor=None):
        super().__init__()
        self._cause = cause
        self._cursor = cursor

    @property
    def cause(self):
        return self._cause

    @property
    def cursor(self):
        return self._cursor


class Recipe:
    def get_visitor(self):
        from .visitor import TreeVisitor
        return TreeVisitor.noop()
