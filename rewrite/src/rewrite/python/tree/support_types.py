from __future__ import annotations

from enum import Enum, auto
from typing import Protocol, TypeVar, runtime_checkable, Any, Optional

from rewrite import Tree, TreeVisitor
from rewrite.java.tree import J


P = TypeVar('P')


@runtime_checkable
class Py(J, Protocol):
    def accept(self, v: TreeVisitor[Any, P], p: P) -> Optional[Any]:
        from rewrite.python.visitor import PythonVisitor
        return self.accept_python(v.adapt(Py, PythonVisitor), p)

    def accept_python(self, v: 'PythonVisitor[P]', p: P) -> Optional['J']:
        ...


class PySpace:
    class Location(Enum):
        ASSERT_STATEMENT_EXPRESSION_SUFFIX = auto()
        ASSERT_STATEMENT_PREFIX = auto()
        AWAIT_EXPRESSION_PREFIX = auto()
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
        PASS_STATEMENT_PREFIX = auto()
        SPECIAL_ARGUMENT_PREFIX = auto()
        SPECIAL_PARAMETER_PREFIX = auto()
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
        COMPILATION_UNIT_STATEMENTS = PySpace.Location.COMPILATION_UNIT_STATEMENT_PREFIX
        DEL_STATEMENT_TARGETS = PySpace.Location.DEL_STATEMENT_TARGET_SUFFIX
        DICT_LITERAL_ELEMENT = PySpace.Location.DICT_LITERAL_ELEMENT_SUFFIX
        KEY_VALUE_KEY = PySpace.Location.DICT_ENTRY_KEY_SUFFIX
        KEY_VALUE_KEY_SUFFIX = PySpace.Location.KEY_VALUE_SUFFIX
        MATCH_CASE_PATTERN_CHILD = PySpace.Location.MATCH_PATTERN_ELEMENT_SUFFIX
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
        DICT_LITERAL_ELEMENTS = (PySpace.Location.DICT_LITERAL_PREFIX, PyRightPadded.Location.DICT_LITERAL_ELEMENT)
        MATCH_CASE_PATTERN_CHILDREN = (PySpace.Location.MATCH_CASE_PATTERN_CHILDREN_PREFIX, PyRightPadded.Location.MATCH_CASE_PATTERN_CHILD)

        def __init__(self, before_location: PySpace.Location, element_location: PyRightPadded.Location):
            self.before_location = before_location
            self.element_location = element_location
