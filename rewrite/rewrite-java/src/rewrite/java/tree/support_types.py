from __future__ import annotations

import weakref
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Protocol, TypeVar, Generic, ClassVar, Dict, runtime_checkable
from uuid import UUID

from rewrite import Tree, SourceFile
from rewrite.marker import Markers


P = TypeVar('P')


@runtime_checkable
class J(Tree, Protocol):
    pass


@dataclass(frozen=True)
class Comment:
    _multiline: bool

    @property
    def multiline(self) -> bool:
        return self._multiline

    def with_multiline(self, multiline: bool) -> Comment:
        return self if multiline is self._multiline else Comment(multiline, self._text, self._suffix, self._markers)

    _text: str

    @property
    def text(self) -> str:
        return self._text

    def with_text(self, text: str) -> Comment:
        return self if text is self._text else Comment(self._multiline, text, self._suffix, self._markers)

    _suffix: str

    @property
    def suffix(self) -> str:
        return self._suffix

    def with_suffix(self, suffix: str) -> Comment:
        return self if suffix is self._suffix else Comment(self._multiline, self._text, suffix, self._markers)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Comment:
        return self if markers is self._markers else Comment(self._multiline, self._text, self._suffix, markers)


@dataclass(frozen=True)
class Space:
    _comments: List[Comment]

    @property
    def comments(self) -> List[Comment]:
        return self._comments

    def with_comments(self, comments: List[Comment]) -> Space:
        return self if comments is self._comments else Space(comments, self._whitespace)

    _whitespace: Optional[str]

    @property
    def whitespace(self) -> Optional[str]:
        return self._whitespace

    def with_whitespace(self, whitespace: Optional[str]) -> Space:
        return self if whitespace is self._whitespace else Space(self._comments, whitespace)

    EMPTY: ClassVar[Space] = None

    class Location(Enum):
        ANY = auto()
        ANNOTATED_TYPE_PREFIX = auto()
        ANNOTATION_ARGUMENTS = auto()
        ANNOTATION_ARGUMENT_SUFFIX = auto()
        ANNOTATIONS = auto()
        ANNOTATION_PREFIX = auto()
        ARRAY_ACCESS_PREFIX = auto()
        ARRAY_INDEX_SUFFIX = auto()
        ARRAY_TYPE_PREFIX = auto()
        ASSERT_PREFIX = auto()
        ASSERT_DETAIL = auto()
        ASSERT_DETAIL_PREFIX = auto()
        ASSIGNMENT = auto()
        ASSIGNMENT_OPERATION_PREFIX = auto()
        ASSIGNMENT_OPERATION_OPERATOR = auto()
        ASSIGNMENT_PREFIX = auto()
        BINARY_OPERATOR = auto()
        BINARY_PREFIX = auto()
        BLOCK_END = auto()
        BLOCK_PREFIX = auto()
        BLOCK_STATEMENT_SUFFIX = auto()
        BREAK_PREFIX = auto()
        CASE = auto()
        CASE_PREFIX = auto()
        CASE_BODY = auto()
        CASE_EXPRESSION = auto()
        CASE_SUFFIX = auto()
        CATCH_ALTERNATIVE_SUFFIX = auto()
        CATCH_PREFIX = auto()
        CLASS_DECLARATION_PREFIX = auto()
        CLASS_KIND = auto()
        COMPILATION_UNIT_EOF = auto()
        COMPILATION_UNIT_PREFIX = auto()
        CONTINUE_PREFIX = auto()
        CONTROL_PARENTHESES_PREFIX = auto()
        DIMENSION_PREFIX = auto()
        DIMENSION = auto()
        DIMENSION_SUFFIX = auto()
        DO_WHILE_PREFIX = auto()
        ELSE_PREFIX = auto()
        EMPTY_PREFIX = auto()
        ENUM_VALUE_PREFIX = auto()
        ENUM_VALUE_SET_PREFIX = auto()
        ENUM_VALUE_SUFFIX = auto()
        EXPRESSION_PREFIX = auto()
        EXTENDS = auto()
        FIELD_ACCESS_NAME = auto()
        FIELD_ACCESS_PREFIX = auto()
        FOREACH_ITERABLE_SUFFIX = auto()
        FOREACH_VARIABLE_SUFFIX = auto()
        FOR_BODY_SUFFIX = auto()
        FOR_CONDITION_SUFFIX = auto()
        FOR_CONTROL_PREFIX = auto()
        FOR_EACH_CONTROL_PREFIX = auto()
        FOR_EACH_LOOP_PREFIX = auto()
        FOR_INIT_SUFFIX = auto()
        FOR_PREFIX = auto()
        FOR_UPDATE_SUFFIX = auto()
        IDENTIFIER_PREFIX = auto()
        IF_ELSE_SUFFIX = auto()
        IF_PREFIX = auto()
        IF_THEN_SUFFIX = auto()
        IMPLEMENTS = auto()
        IMPORT_ALIAS_PREFIX = auto()
        PERMITS = auto()
        IMPLEMENTS_SUFFIX = auto()
        IMPORT_PREFIX = auto()
        IMPORT_SUFFIX = auto()
        INSTANCEOF_PREFIX = auto()
        INSTANCEOF_SUFFIX = auto()
        INTERSECTION_TYPE_PREFIX = auto()
        LABEL_PREFIX = auto()
        LABEL_SUFFIX = auto()
        LAMBDA_ARROW_PREFIX = auto()
        LAMBDA_PARAMETER = auto()
        LAMBDA_PARAMETERS_PREFIX = auto()
        LAMBDA_PREFIX = auto()
        LANGUAGE_EXTENSION = auto()
        LITERAL_PREFIX = auto()
        MEMBER_REFERENCE_CONTAINING = auto()
        MEMBER_REFERENCE_NAME = auto()
        MEMBER_REFERENCE_PREFIX = auto()
        METHOD_DECLARATION_PARAMETERS = auto()
        METHOD_DECLARATION_PARAMETER_SUFFIX = auto()
        METHOD_DECLARATION_DEFAULT_VALUE = auto()
        METHOD_DECLARATION_PREFIX = auto()
        METHOD_INVOCATION_ARGUMENTS = auto()
        METHOD_INVOCATION_ARGUMENT_SUFFIX = auto()
        METHOD_INVOCATION_NAME = auto()
        METHOD_INVOCATION_PREFIX = auto()
        METHOD_SELECT_SUFFIX = auto()
        MODIFIER_PREFIX = auto()
        MULTI_CATCH_PREFIX = auto()
        NAMED_VARIABLE_SUFFIX = auto()
        NEW_ARRAY_INITIALIZER = auto()
        NEW_ARRAY_INITIALIZER_SUFFIX = auto()
        NEW_ARRAY_PREFIX = auto()
        NEW_CLASS_ARGUMENTS = auto()
        NEW_CLASS_ARGUMENTS_SUFFIX = auto()
        NEW_CLASS_ENCLOSING_SUFFIX = auto()
        NEW_CLASS_PREFIX = auto()
        NEW_PREFIX = auto()
        NULLABLE_TYPE_PREFIX = auto()
        NULLABLE_TYPE_SUFFIX = auto()
        PACKAGE_PREFIX = auto()
        PACKAGE_SUFFIX = auto()
        PARAMETERIZED_TYPE_PREFIX = auto()
        PARENTHESES_PREFIX = auto()
        PARENTHESES_SUFFIX = auto()
        PERMITS_SUFFIX = auto()
        PRIMITIVE_PREFIX = auto()
        RECORD_STATE_VECTOR = auto()
        RECORD_STATE_VECTOR_SUFFIX = auto()
        RETURN_PREFIX = auto()
        STATEMENT_PREFIX = auto()
        STATIC_IMPORT = auto()
        STATIC_INIT_SUFFIX = auto()
        SWITCH_PREFIX = auto()
        SWITCH_EXPRESSION_PREFIX = auto()
        SYNCHRONIZED_PREFIX = auto()
        TERNARY_FALSE = auto()
        TERNARY_PREFIX = auto()
        TERNARY_TRUE = auto()
        THROWS = auto()
        THROWS_SUFFIX = auto()
        THROW_PREFIX = auto()
        TRY_FINALLY = auto()
        TRY_PREFIX = auto()
        TRY_RESOURCE = auto()
        TRY_RESOURCES = auto()
        TRY_RESOURCE_SUFFIX = auto()
        TYPE_BOUNDS = auto()
        TYPE_BOUND_SUFFIX = auto()
        TYPE_CAST_PREFIX = auto()
        TYPE_PARAMETERS = auto()
        TYPE_PARAMETERS_PREFIX = auto()
        TYPE_PARAMETER_SUFFIX = auto()
        UNARY_OPERATOR = auto()
        UNARY_PREFIX = auto()
        UNKNOWN_PREFIX = auto()
        UNKNOWN_SOURCE_PREFIX = auto()
        VARARGS = auto()
        VARIABLE_DECLARATIONS_PREFIX = auto()
        VARIABLE_INITIALIZER = auto()
        VARIABLE_PREFIX = auto()
        WHILE_BODY_SUFFIX = auto()
        WHILE_CONDITION = auto()
        WHILE_PREFIX = auto()
        WILDCARD_BOUND = auto()
        WILDCARD_PREFIX = auto()
        YIELD_PREFIX = auto()


Space.EMPTY = Space([], '')


class JavaSourceFile(SourceFile, Protocol):
    pass


class Expression(J, Protocol):
    pass


class Statement(J, Protocol):
    pass


class TypedTree(J, Protocol):
    pass


class NameTree(TypedTree, Protocol):
    pass


class TypeTree(NameTree, Protocol):
    pass


class Loop(Tree, Protocol):
    pass


class MethodCall(Tree, Protocol):
    pass


class JavaType(Protocol):
    pass


T = TypeVar('T')
J2 = TypeVar('J2', bound=J)


@dataclass(frozen=True)
class JRightPadded(Generic[T]):
    _element: T

    @property
    def element(self) -> T:
        return self._element

    def with_element(self, element: T) -> JRightPadded[T]:
        return self if element is self._element else JRightPadded(element, self._after, self._markers)

    _after: Space

    @property
    def after(self) -> Space:
        return self._after

    def with_after(self, after: Space) -> JRightPadded[T]:
        return self if after is self._after else JRightPadded(self._element, after, self._markers)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> JRightPadded[T]:
        return self if markers is self._markers else JRightPadded(self._element, self._after, markers)

    @classmethod
    def get_elements(cls, padded_list: List[JRightPadded[T]]) -> List[T]:
        return [x.element for x in padded_list]

    @classmethod
    def with_elements(cls, before: List[JRightPadded[J2]], elements: List[J2]) -> List[JRightPadded[J2]]:
        # a cheaper check for the most common case when there are no changes
        if len(elements) == len(before):
            has_changes = False
            for i in range(len(before)):
                if before[i].element != elements[i]:
                    has_changes = True
                    break
            if not has_changes:
                return before
        elif not elements:
            return []

        after: List[JRightPadded[J2]] = []
        before_by_id: Dict[UUID, JRightPadded[J2]] = {}

        for j in before:
            if j.element.id in before_by_id:
                raise Exception("Duplicate key")
            before_by_id[j.element.id] = j

        for t in elements:
            found = before_by_id.get(t.id)
            if found is not None:
                after.append(found.with_element(t))
            else:
                after.append(JRightPadded(t, Space.EMPTY, Markers.EMPTY))

        return after

    class Location(Enum):
        ANNOTATION_ARGUMENT = Space.Location.ANNOTATION_ARGUMENT_SUFFIX
        ARRAY_INDEX = Space.Location.ARRAY_INDEX_SUFFIX
        BLOCK_STATEMENT = Space.Location.BLOCK_STATEMENT_SUFFIX
        CASE = Space.Location.CASE_SUFFIX
        CASE_BODY = Space.Location.CASE_BODY
        CASE_EXPRESSION = Space.Location.CASE_EXPRESSION
        CATCH_ALTERNATIVE = Space.Location.CATCH_ALTERNATIVE_SUFFIX
        DIMENSION = Space.Location.DIMENSION_SUFFIX
        ENUM_VALUE = Space.Location.ENUM_VALUE_SUFFIX
        FOREACH_ITERABLE = Space.Location.FOREACH_ITERABLE_SUFFIX
        FOREACH_VARIABLE = Space.Location.FOREACH_VARIABLE_SUFFIX
        FOR_BODY = Space.Location.FOR_BODY_SUFFIX
        FOR_CONDITION = Space.Location.FOR_CONDITION_SUFFIX
        FOR_INIT = Space.Location.FOR_INIT_SUFFIX
        FOR_UPDATE = Space.Location.FOR_UPDATE_SUFFIX
        IF_ELSE = Space.Location.IF_ELSE_SUFFIX
        IF_THEN = Space.Location.IF_THEN_SUFFIX
        IMPLEMENTS = Space.Location.IMPLEMENTS_SUFFIX
        IMPORT = Space.Location.IMPORT_SUFFIX
        INSTANCEOF = Space.Location.INSTANCEOF_SUFFIX
        LABEL = Space.Location.LABEL_SUFFIX
        LAMBDA_PARAM = Space.Location.LAMBDA_PARAMETER
        LANGUAGE_EXTENSION = Space.Location.LANGUAGE_EXTENSION
        MEMBER_REFERENCE_CONTAINING = Space.Location.MEMBER_REFERENCE_CONTAINING
        METHOD_DECLARATION_PARAMETER = Space.Location.METHOD_DECLARATION_PARAMETER_SUFFIX
        METHOD_INVOCATION_ARGUMENT = Space.Location.METHOD_INVOCATION_ARGUMENT_SUFFIX
        METHOD_SELECT = Space.Location.METHOD_SELECT_SUFFIX
        NAMED_VARIABLE = Space.Location.NAMED_VARIABLE_SUFFIX
        NEW_ARRAY_INITIALIZER = Space.Location.NEW_ARRAY_INITIALIZER_SUFFIX
        NEW_CLASS_ARGUMENTS = Space.Location.NEW_CLASS_ARGUMENTS_SUFFIX
        NEW_CLASS_ENCLOSING = Space.Location.NEW_CLASS_ENCLOSING_SUFFIX
        NULLABLE = Space.Location.NULLABLE_TYPE_SUFFIX
        PACKAGE = Space.Location.PACKAGE_SUFFIX
        PARENTHESES = Space.Location.PARENTHESES_SUFFIX
        PERMITS = Space.Location.PERMITS_SUFFIX
        RECORD_STATE_VECTOR = Space.Location.RECORD_STATE_VECTOR_SUFFIX
        STATIC_INIT = Space.Location.STATIC_INIT_SUFFIX
        THROWS = Space.Location.THROWS_SUFFIX
        TRY_RESOURCE = Space.Location.TRY_RESOURCE_SUFFIX
        TYPE_BOUND = Space.Location.TYPE_BOUND_SUFFIX
        TYPE_PARAMETER = Space.Location.TYPE_PARAMETER_SUFFIX
        WHILE_BODY = Space.Location.WHILE_BODY_SUFFIX

        def __init__(self, after_location: Space.Location):
            self.after_location = after_location

@dataclass(frozen=True)
class JLeftPadded(Generic[T]):
    _before: Space

    @property
    def before(self) -> Space:
        return self._before

    def with_before(self, before: Space) -> JLeftPadded[T]:
        return self if before is self._before else JLeftPadded(before, self._element, self._markers)

    _element: T

    @property
    def element(self) -> T:
        return self._element

    def with_element(self, element: T) -> JLeftPadded[T]:
        return self if element is self._element else JLeftPadded(self._before, element, self._markers)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> JLeftPadded[T]:
        return self if markers is self._markers else JLeftPadded(self._before, self._element, markers)

    class Location(Enum):
        ARRAY_TYPE_DIMENSION = Space.Location.DIMENSION_PREFIX
        ASSERT_DETAIL = Space.Location.ASSERT_DETAIL_PREFIX
        ASSIGNMENT = Space.Location.ASSIGNMENT
        ASSIGNMENT_OPERATION_OPERATOR = Space.Location.ASSIGNMENT_OPERATION_OPERATOR
        BINARY_OPERATOR = Space.Location.BINARY_OPERATOR
        CLASS_KIND = Space.Location.CLASS_KIND
        DIMENSION_PREFIX = Space.Location.CLASS_KIND
        EXTENDS = Space.Location.EXTENDS
        FIELD_ACCESS_NAME = Space.Location.FIELD_ACCESS_NAME
        IMPORT_ALIAS_PREFIX = Space.Location.IMPORT_ALIAS_PREFIX
        LANGUAGE_EXTENSION = Space.Location.LANGUAGE_EXTENSION
        MEMBER_REFERENCE_NAME = Space.Location.MEMBER_REFERENCE_NAME
        METHOD_DECLARATION_DEFAULT_VALUE = Space.Location.METHOD_DECLARATION_DEFAULT_VALUE
        STATIC_IMPORT = Space.Location.STATIC_IMPORT
        TERNARY_FALSE = Space.Location.TERNARY_FALSE
        TERNARY_TRUE = Space.Location.TERNARY_TRUE
        TRY_FINALLY = Space.Location.TRY_FINALLY
        UNARY_OPERATOR = Space.Location.UNARY_OPERATOR
        VARIABLE_INITIALIZER = Space.Location.VARIABLE_INITIALIZER
        WHILE_CONDITION = Space.Location.WHILE_CONDITION
        WILDCARD_BOUND = Space.Location.WILDCARD_BOUND

        def __init__(self, before_location: Space.Location):
            self.before_location = before_location


@dataclass(frozen=True)
class JContainer(Generic[T]):
    _before: Space

    @property
    def before(self) -> Space:
        return self._before

    def with_before(self, before: Space) -> JContainer[T]:
        return self if before is self._before else JContainer(before, self._elements, self._markers)

    _elements: List[JRightPadded[T]]

    @property
    def elements(self) -> List[T]:
        return JRightPadded.get_elements(self._elements)

    def with_elements(self, elements: List[T]) -> JContainer[T]:
        return self.padding.with_elements(JRightPadded.with_elements(self._elements, elements))

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> JContainer[T]:
        return self if markers is self._markers else JContainer(self._before, self._elements, markers)

    @dataclass
    class PaddingHelper:
        _t: JContainer[T]

        @property
        def elements(self) -> List[JRightPadded[T]]:
            return self._t._elements

        def with_elements(self, elements: List[JRightPadded[T]]) -> JContainer[T]:
            return self._t if self._t._elements is elements else JContainer(self._t._before, elements, self._t._markers)

    _padding: weakref.ReferenceType[JContainer.PaddingHelper] = None

    @property
    def padding(self) -> JContainer.PaddingHelper:
        p: JContainer.PaddingHelper
        if self._padding is None:
            p = JContainer.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            # noinspection PyProtectedMember
            if p is None or p._t != self:
                p = JContainer.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    @classmethod
    def with_elements_nullable(cls, before: Optional[JContainer[J2]], elements: Optional[List[J2]]) -> Optional[
        JContainer[J2]]:
        if elements is None or elements == []:
            return None
        if before is None:
            return JContainer(Space.EMPTY, elements, Markers.EMPTY)
        return before.padding.with_elements(JRightPadded.with_elements(before._elements, elements))

    class Location(Enum):
        ANNOTATION_ARGUMENTS = (Space.Location.ANNOTATION_ARGUMENTS, JRightPadded.Location.ANNOTATION_ARGUMENT)
        CASE = (Space.Location.CASE, JRightPadded.Location.CASE)
        CASE_EXPRESSION = (Space.Location.CASE_EXPRESSION, JRightPadded.Location.CASE_EXPRESSION)
        IMPLEMENTS = (Space.Location.IMPLEMENTS, JRightPadded.Location.IMPLEMENTS)
        LANGUAGE_EXTENSION = (Space.Location.LANGUAGE_EXTENSION, JRightPadded.Location.LANGUAGE_EXTENSION)
        METHOD_DECLARATION_PARAMETERS = (Space.Location.METHOD_DECLARATION_PARAMETERS, JRightPadded.Location.METHOD_DECLARATION_PARAMETER)
        METHOD_INVOCATION_ARGUMENTS = (Space.Location.METHOD_INVOCATION_ARGUMENTS, JRightPadded.Location.METHOD_INVOCATION_ARGUMENT)
        NEW_ARRAY_INITIALIZER = (Space.Location.NEW_ARRAY_INITIALIZER, JRightPadded.Location.NEW_ARRAY_INITIALIZER)
        NEW_CLASS_ARGUMENTS = (Space.Location.NEW_CLASS_ARGUMENTS, JRightPadded.Location.NEW_CLASS_ARGUMENTS)
        PERMITS = (Space.Location.PERMITS, JRightPadded.Location.PERMITS)
        RECORD_STATE_VECTOR = (Space.Location.RECORD_STATE_VECTOR, JRightPadded.Location.RECORD_STATE_VECTOR)
        THROWS = (Space.Location.THROWS, JRightPadded.Location.THROWS)
        TRY_RESOURCES = (Space.Location.TRY_RESOURCES, JRightPadded.Location.TRY_RESOURCE)
        TYPE_BOUNDS = (Space.Location.TYPE_BOUNDS, JRightPadded.Location.TYPE_BOUND)
        TYPE_PARAMETERS = (Space.Location.TYPE_PARAMETERS, JRightPadded.Location.TYPE_PARAMETER)

        def __init__(self, before_location: Space.Location, element_location: JRightPadded.Location):
            self.before_location = before_location
            self.element_location = element_location
