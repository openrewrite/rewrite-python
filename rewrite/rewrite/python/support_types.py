from __future__ import annotations

from dataclasses import replace, dataclass
from enum import Enum, auto
from typing import Protocol, TypeVar, runtime_checkable, Any, Optional, TYPE_CHECKING

from rewrite import TreeVisitor, Markers
from rewrite.java.tree import J
from ..java import Comment

if TYPE_CHECKING:
    from .visitor import PythonVisitor

P = TypeVar('P')


@runtime_checkable
class Py(J, Protocol):
    def accept(self, v: TreeVisitor[Any, P], p: P) -> Optional[Any]:
        from .visitor import PythonVisitor
        return self.accept_python(v.adapt(Py, PythonVisitor), p)

    def accept_python(self, v: 'PythonVisitor[P]', p: P) -> Optional['J']:
        ...


class PySpace:
    class Location(Enum):
        ASSERT_STATEMENT_EXPRESSION_SUFFIX = auto()
        ASSERT_STATEMENT_PREFIX = auto()
        AWAIT_EXPRESSION_PREFIX = auto()
        COLLECTION_LITERAL_ELEMENT_SUFFIX = auto()
        COLLECTION_LITERAL_PREFIX = auto()
        COMPILATION_UNIT_STATEMENT_PREFIX = auto()
        COMPREHENSION_EXPRESSION_CLAUSE_ITERATED_LIST = auto()
        COMPREHENSION_EXPRESSION_CLAUSE_PREFIX = auto()
        COMPREHENSION_EXPRESSION_CONDITION_PREFIX = auto()
        COMPREHENSION_EXPRESSION_PREFIX = auto()
        COMPREHENSION_EXPRESSION_SUFFIX = auto()
        COMPREHENSION_IN = auto()
        DEL_STATEMENT_PREFIX = auto()
        DEL_STATEMENT_TARGET_SUFFIX = auto()
        DICT_ENTRY = auto()
        DICT_ENTRY_KEY_SUFFIX = auto()
        DICT_LITERAL_ELEMENT_SUFFIX = auto()
        DICT_LITERAL_PREFIX = auto()
        ELSE_WRAPPER_ELSE_BLOCK_PREFIX = auto()
        ELSE_WRAPPER_PREFIX = auto()
        ERROR_FROM_EXPRESSION_FROM_PREFIX = auto()
        ERROR_FROM_EXPRESSION_PREFIX = auto()
        EXCEPTION_TYPE_PREFIX = auto()
        KEY_VALUE_PREFIX = auto()
        KEY_VALUE_SUFFIX = auto()
        MATCH_CASE_GUARD = auto()
        MATCH_CASE_PATTERN_CHILDREN_PREFIX = auto()
        MATCH_CASE_PATTERN_PREFIX = auto()
        MATCH_CASE_PREFIX = auto()
        MATCH_PATTERN_ELEMENT_SUFFIX = auto()
        MATCH_PATTERN_PREFIX = auto()
        NAMED_ARGUMENT = auto()
        NAMED_ARGUMENT_PREFIX = auto()
        PASS_PREFIX = auto()
        SLICE_EXPRESSION_PREFIX = auto()
        SLICE_EXPRESSION_START_SUFFIX = auto()
        SLICE_EXPRESSION_STEP_SUFFIX = auto()
        SLICE_EXPRESSION_STOP_SUFFIX = auto()
        SPECIAL_PARAMETER_PREFIX = auto()
        STAR_EXPRESSION_PREFIX = auto()
        TOP_LEVEL_STATEMENT = auto()
        TRAILING_ELSE_WRAPPER_PREFIX = auto()
        TYPE_HINTED_EXPRESSION_PREFIX = auto()
        TYPE_HINT_PREFIX = auto()
        VARIABLE_SCOPE_STATEMENT_NAME_SUFFIX = auto()
        VARIABLE_SCOPE_STATEMENT_PREFIX = auto()
        YIELD_EXPRESSION_EXPRESSION_SUFFIX = auto()
        YIELD_EXPRESSION_FROM_PREFIX = auto()
        YIELD_EXPRESSION_PREFIX = auto()


T = TypeVar('T')
J2 = TypeVar('J2', bound=J)


class PyRightPadded:
    class Location(Enum):
        ASSERT_STATEMENT_EXPRESSIONS = PySpace.Location.ASSERT_STATEMENT_EXPRESSION_SUFFIX
        COLLECTION_LITERAL_ELEMENT = PySpace.Location.COLLECTION_LITERAL_ELEMENT_SUFFIX
        COMPILATION_UNIT_STATEMENTS = PySpace.Location.COMPILATION_UNIT_STATEMENT_PREFIX
        DEL_STATEMENT_TARGETS = PySpace.Location.DEL_STATEMENT_TARGET_SUFFIX
        DICT_LITERAL_ELEMENT = PySpace.Location.DICT_LITERAL_ELEMENT_SUFFIX
        KEY_VALUE_KEY = PySpace.Location.DICT_ENTRY_KEY_SUFFIX
        KEY_VALUE_KEY_SUFFIX = PySpace.Location.KEY_VALUE_SUFFIX
        MATCH_CASE_PATTERN_CHILD = PySpace.Location.MATCH_PATTERN_ELEMENT_SUFFIX
        SLICE_EXPRESSION_START = PySpace.Location.SLICE_EXPRESSION_START_SUFFIX
        SLICE_EXPRESSION_STEP = PySpace.Location.SLICE_EXPRESSION_STEP_SUFFIX
        SLICE_EXPRESSION_STOP = PySpace.Location.SLICE_EXPRESSION_STOP_SUFFIX
        TOP_LEVEL_STATEMENT_SUFFIX = PySpace.Location.TOP_LEVEL_STATEMENT
        VARIABLE_SCOPE_STATEMENT_NAMES = PySpace.Location.VARIABLE_SCOPE_STATEMENT_NAME_SUFFIX
        YIELD_EXPRESSION_EXPRESSIONS = PySpace.Location.YIELD_EXPRESSION_EXPRESSION_SUFFIX

        def __init__(self, after_location: PySpace.Location):
            self.after_location = after_location


class PyLeftPadded:
    class Location(Enum):
        COMPREHENSION_EXPRESSION_CLAUSE_ITERATED_LIST = PySpace.Location.COMPREHENSION_EXPRESSION_CLAUSE_ITERATED_LIST
        ERROR_FROM_EXPRESSION_FROM = PySpace.Location.ERROR_FROM_EXPRESSION_FROM_PREFIX
        MATCH_CASE_GUARD = PySpace.Location.MATCH_CASE_GUARD
        NAMED_ARGUMENT_VALUE = PySpace.Location.NAMED_ARGUMENT
        TRAILING_ELSE_WRAPPER_ELSE_BLOCK = PySpace.Location.ELSE_WRAPPER_ELSE_BLOCK_PREFIX
        YIELD_EXPRESSION_FROM = PySpace.Location.YIELD_EXPRESSION_FROM_PREFIX

        def __init__(self, before_location: PySpace.Location):
            self.before_location = before_location


class PyContainer:
    class Location(Enum):
        COLLECTION_LITERAL_ELEMENTS = (PySpace.Location.COLLECTION_LITERAL_PREFIX, PyRightPadded.Location.COLLECTION_LITERAL_ELEMENT)
        DICT_LITERAL_ELEMENTS = (PySpace.Location.DICT_LITERAL_PREFIX, PyRightPadded.Location.DICT_LITERAL_ELEMENT)
        MATCH_CASE_PATTERN_CHILDREN = (PySpace.Location.MATCH_CASE_PATTERN_CHILDREN_PREFIX, PyRightPadded.Location.MATCH_CASE_PATTERN_CHILD)

        def __init__(self, before_location: PySpace.Location, element_location: PyRightPadded.Location):
            self.before_location = before_location
            self.element_location = element_location


@dataclass(frozen=True)
class PyComment(Comment):

    _aligned_to_indent: bool

    @property
    def aligned_to_indent(self) -> bool:
        return self._aligned_to_indent

    def with_aligned_to_indent(self, aligned_to_indent: bool) -> Comment:
        return self if aligned_to_indent is self._aligned_to_indent else replace(self, _aligned_to_indent=aligned_to_indent)

    @property
    def multiline(self) -> bool:
        return False

    # IMPORTANT: This explicit constructor aligns the parameter order with the Java side
    def __init__(self, text: str, suffix: str, aligned_to_indent: bool, markers: Markers) -> None:
        object.__setattr__(self, '_text', text)
        object.__setattr__(self, '_suffix', suffix)
        object.__setattr__(self, '_aligned_to_indent', aligned_to_indent)
        object.__setattr__(self, '_markers', markers)
