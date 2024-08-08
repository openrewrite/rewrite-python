from __future__ import annotations

import weakref
from enum import Enum, auto
from typing import List, Optional, Protocol, TypeVar, Generic, ClassVar, Dict
from uuid import UUID

from attr import dataclass

from rewrite.core import Tree, SourceFile
from rewrite.core.marker import Markers
from rewrite.java.tree.tree import J


class PySpace:
    class Location(Enum):
        ASSERT_PREFIX = auto()
        ASSERT_ELEMENT_SUFFIX = auto()
        AWAIT_PREFIX = auto()
        COMPREHENSION_CLAUSE_PREFIX = auto()
        COMPREHENSION_CONDITION_PREFIX = auto()
        COMPREHENSION_IN = auto()
        COMPREHENSION_PREFIX = auto()
        COMPREHENSION_SUFFIX = auto()
        NAMED_ARGUMENT_PREFIX = auto()
        DEL_ELEMENT_SUFFIX = auto()
        DEL_PREFIX = auto()
        DICT_ENTRY = auto()
        DICT_ENTRY_KEY_SUFFIX = auto()
        DICT_LITERAL_ELEMENT_SUFFIX = auto()
        DICT_LITERAL_PREFIX = auto()
        ELSE_WRAPPER_PREFIX = auto()
        EXCEPTION_TYPE_PREFIX = auto()
        ERROR_FROM_PREFIX = auto()
        ERROR_FROM_SOURCE = auto()
        KEY_VALUE_PREFIX = auto()
        KEY_VALUE_SUFFIX = auto()
        MATCH_CASE_GUARD = auto()
        MATCH_CASE_PREFIX = auto()
        MATCH_PATTERN_PREFIX = auto()
        MATCH_PATTERN_ELEMENT_PREFIX = auto()
        MATCH_PATTERN_ELEMENT_SUFFIX = auto()
        NAMED_ARGUMENT = auto()
        PASS_PREFIX = auto()
        SPECIAL_ARG_PREFIX = auto()
        SPECIAL_PARAM_PREFIX = auto()
        TOP_LEVEL_STATEMENT = auto()
        TRAILING_ELSE_WRAPPER_PREFIX = auto()
        TYPE_HINT_PREFIX = auto()
        TYPE_HINTED_EXPRESSION_PREFIX = auto()
        VARIABLE_SCOPE_NAME_SUFFIX = auto()
        VARIABLE_SCOPE_PREFIX = auto()
        YIELD_FROM_PREFIX = auto()
        YIELD_PREFIX = auto()
        YIELD_ELEMENT_SUFFIX = auto()


T = TypeVar('T')
J2 = TypeVar('J2', bound=J)


class PyRightPadded:
    class Location(Emum):
        ANNOTATION_ARGUMENT = PySpace.Location.ANNOTATION_ARGUMENT_SUFFIX


class PyLeftPadded:
    class Location(Enum):
        ERROR_FROM = PySpace.Location.ERROR_FROM_SOURCE
        MATCH_CASE_GUARD = PySpace.Location.MATCH_CASE_GUARD
        NAMED_ARGUMENT = PySpace.Location.NAMED_ARGUMENT
        YIELD_FROM = PySpace.Location.YIELD_FROM_PREFIX

        def __init__(self, before_location: PySpace.Location):
            self.before_location = before_location

        before_location: PySpace.Location = None


class PyContainer:
    class Location(Enum):
        DICT_LITERAL_ELEMENTS = (PySpace.Location.DICT_LITERAL_PREFIX, PyRightPadded.Location.DICT_LITERAL_ELEMENT)
        MATCH_PATTERN_ELEMENTS = (PySpace.Location.MATCH_PATTERN_ELEMENT_PREFIX, PyRightPadded.Location.MATCH_PATTERN_ELEMENT)

        def __init__(self, before_location: PySpace.Location, element_location: PyRightPadded.Location):
            self.before_location = before_location
            self.element_location = element_location

        before_location: PySpace.Location = None
        element_location: PyRightPadded.Location = None
