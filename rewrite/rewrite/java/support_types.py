from __future__ import annotations

import weakref
from abc import abstractmethod, ABC
from dataclasses import dataclass, replace
from enum import Enum, auto
from typing import List, Optional, TypeVar, Generic, ClassVar, Dict, Any, TYPE_CHECKING, Iterable, cast
from uuid import UUID

from rewrite import Markers
from rewrite import Tree, SourceFile, TreeVisitor

if TYPE_CHECKING:
    from .visitor import JavaVisitor

P = TypeVar('P')


class J(Tree):
    @property
    @abstractmethod
    def prefix(self) -> Space:
        ...

    @abstractmethod
    def with_prefix(self, prefix: Space) -> 'J':
        ...

    def is_acceptable(self, v: TreeVisitor[Any, P], p: P) -> bool:
        from .visitor import JavaVisitor
        return isinstance(v, JavaVisitor)

    def accept(self, v: TreeVisitor[Any, P], p: P) -> Optional[Any]:
        from .visitor import JavaVisitor
        return self.accept_java(v.adapt(J, JavaVisitor), p)

    def accept_java(self, v: 'JavaVisitor[P]', p: P) -> Optional['J']:
        ...


@dataclass(frozen=True)
class Comment(ABC):
    @property
    @abstractmethod
    def multiline(self) -> bool:
        ...

    _text: str

    @property
    def text(self) -> str:
        return self._text

    def with_text(self, text: str) -> Comment:
        return self if text is self._text else replace(self, _text=text)

    _suffix: str

    @property
    def suffix(self) -> str:
        return self._suffix

    def with_suffix(self, suffix: str) -> Comment:
        return self if suffix is self._suffix else replace(self, _suffix=suffix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Comment:
        return self if markers is self._markers else replace(self, _markers=markers)


@dataclass(frozen=True)
class TextComment(Comment):
    _multiline: bool

    @property
    def multiline(self) -> bool:
        return self._multiline

    def with_multiline(self, multiline: bool) -> Comment:
        return self if multiline is self._multiline else replace(self, _multiline=multiline)

    # IMPORTANT: This explicit constructor aligns the parameter order with the Java side
    def __init__(self, _multiline: bool, _text: str, _suffix: str, _markers: Markers) -> None:
        object.__setattr__(self, '_multiline', _multiline)
        object.__setattr__(self, '_text', _text)
        object.__setattr__(self, '_suffix', _suffix)
        object.__setattr__(self, '_markers', _markers)


@dataclass(frozen=True)
class Space:
    _comments: List[Comment]

    @property
    def comments(self) -> List[Comment]:
        return self._comments

    def with_comments(self, comments: List[Comment]) -> Space:
        return self if comments is self._comments else replace(self, _comments=comments)

    _whitespace: Optional[str]

    @property
    def whitespace(self) -> str:
        return self._whitespace if self._whitespace is not None else ""

    def with_whitespace(self, whitespace: Optional[str]) -> Space:
        return self if whitespace is self._whitespace else replace(self, _whitespace=whitespace)

    def is_empty(self) -> bool:
        return len(self._comments) == 0 and (self._whitespace is None or self._whitespace == '')

    @classmethod
    def first_prefix(cls, trees: Optional[Iterable[J]]) -> Space:
        return Space.EMPTY if trees is None or not trees else next(iter(trees)).prefix

    @classmethod
    def format_first_prefix(cls, trees: List[J2], prefix: Space) -> List[J2]:
        if trees and next(iter(trees)).prefix != prefix:
            formatted_trees = list(trees)
            formatted_trees[0] = cast(J2, formatted_trees[0].with_prefix(prefix))
            return formatted_trees
        return trees

    @property
    def indent(self) -> str:
        """
        The indentation after the last newline of either the last comment's suffix
        or the global whitespace if no comments exist.
        """
        return self._get_whitespace_indent(self.last_whitespace)

    @property
    def last_whitespace(self) -> str:
        """
        The raw suffix from the last comment if it exists, otherwise the global
        whitespace (or empty string if whitespace is None).
        """
        if self._comments:
            return self._comments[-1].suffix
        return self._whitespace if self._whitespace is not None else ""

    @staticmethod
    def _get_whitespace_indent(whitespace: Optional[str]) -> str:
        """
        A helper method that extracts everything after the last newline character
        in `whitespace`. If no newline is present, returns `whitespace` as-is.
        If the last newline is at the end, returns an empty string.
        """
        if not whitespace:
            return ""
        last_newline = whitespace.rfind('\n')
        return whitespace if last_newline == -1 else whitespace[last_newline + 1:]

    EMPTY: ClassVar[Space]
    SINGLE_SPACE: ClassVar[Space]

    class Location(Enum):
        ANNOTATED_TYPE_PREFIX = auto()
        ANNOTATIONS = auto()
        ANNOTATION_ARGUMENTS = auto()
        ANNOTATION_ARGUMENT_SUFFIX = auto()
        ANNOTATION_PREFIX = auto()
        ANY = auto()
        ARRAY_ACCESS_PREFIX = auto()
        ARRAY_INDEX_SUFFIX = auto()
        ARRAY_TYPE_PREFIX = auto()
        ASSERT_DETAIL = auto()
        ASSERT_DETAIL_PREFIX = auto()
        ASSERT_PREFIX = auto()
        ASSIGNMENT = auto()
        ASSIGNMENT_OPERATION_OPERATOR = auto()
        ASSIGNMENT_OPERATION_PREFIX = auto()
        ASSIGNMENT_PREFIX = auto()
        BINARY_OPERATOR = auto()
        BINARY_PREFIX = auto()
        BLOCK_END = auto()
        BLOCK_PREFIX = auto()
        BLOCK_STATEMENT_SUFFIX = auto()
        BREAK_PREFIX = auto()
        CASE = auto()
        CASE_BODY = auto()
        CASE_EXPRESSION = auto()
        CASE_PREFIX = auto()
        CASE_SUFFIX = auto()
        CATCH_ALTERNATIVE_SUFFIX = auto()
        CATCH_PREFIX = auto()
        CLASS_DECLARATION_PREFIX = auto()
        CLASS_KIND = auto()
        COMPILATION_UNIT_EOF = auto()
        COMPILATION_UNIT_PREFIX = auto()
        CONTINUE_PREFIX = auto()
        CONTROL_PARENTHESES_PREFIX = auto()
        DIMENSION = auto()
        DIMENSION_PREFIX = auto()
        DIMENSION_SUFFIX = auto()
        DO_WHILE_PREFIX = auto()
        ELSE_PREFIX = auto()
        EMPTY_PREFIX = auto()
        ENUM_VALUE_PREFIX = auto()
        ENUM_VALUE_SET_PREFIX = auto()
        ENUM_VALUE_SUFFIX = auto()
        ERRONEOUS_PREFIX = auto()
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
        IMPLEMENTS_SUFFIX = auto()
        IMPORT_ALIAS_PREFIX = auto()
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
        METHOD_DECLARATION_DEFAULT_VALUE = auto()
        METHOD_DECLARATION_PARAMETERS = auto()
        METHOD_DECLARATION_PARAMETER_SUFFIX = auto()
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
        PERMITS = auto()
        PERMITS_SUFFIX = auto()
        PRIMITIVE_PREFIX = auto()
        RECORD_STATE_VECTOR = auto()
        RECORD_STATE_VECTOR_SUFFIX = auto()
        RETURN_PREFIX = auto()
        STATEMENT_PREFIX = auto()
        STATIC_IMPORT = auto()
        STATIC_INIT_SUFFIX = auto()
        SWITCH_EXPRESSION_PREFIX = auto()
        SWITCH_PREFIX = auto()
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
Space.SINGLE_SPACE = Space([], ' ')


class JavaSourceFile(J, SourceFile):
    pass


class Expression(J):
    pass


class Statement(J):
    pass


class TypedTree(J):
    pass


class NameTree(TypedTree):
    pass


class TypeTree(NameTree):
    pass


class Loop(Statement):
    pass


class MethodCall(Expression):
    pass


class JavaType(ABC):
    class FullyQualified:
        class Kind(Enum):
            Class = 0
            Enum = 1
            Interface = 2
            Annotation = 3
            Record = 4

    class Unknown(FullyQualified):
        pass

    class Class(FullyQualified):
        pass

    class ShallowClass(Class):
        pass

    class Parameterized(FullyQualified):
        pass

    class GenericTypeVariable:
        class Variance(Enum):
            Invariant = 0
            Covariant = 1
            Contravariant = 2

    class Primitive(Enum):
        Boolean = 0
        Byte = 1
        Char = 2
        Double = 3
        Float = 4
        Int = 5
        Long = 6
        Short = 7
        Void = 8
        String = 9
        None_ = 10
        Null = 11

    class Method:
        pass

    class Variable:
        pass

    class Array:
        pass


T = TypeVar('T')
J2 = TypeVar('J2', bound=J)
J3 = TypeVar('J3', bound=J)


@dataclass(frozen=True)
class JRightPadded(Generic[T]):
    _element: T

    @property
    def element(self) -> T:
        return self._element

    def with_element(self, element: T) -> JRightPadded[T]:
        return self if element is self._element else replace(self, _element=element)

    _after: Space

    @property
    def after(self) -> Space:
        return self._after

    def with_after(self, after: Space) -> JRightPadded[T]:
        return self if after is self._after else replace(self, _after=after)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> JRightPadded[T]:
        return self if markers is self._markers else replace(self, _markers=markers)

    @classmethod
    def get_elements(cls, padded_list: List[JRightPadded[T]]) -> List[T]:
        return [x.element for x in padded_list]

    @classmethod
    def with_elements(cls, before: List[JRightPadded[J2]], elements: List[J2]) -> List[JRightPadded[J2]]:
        # a cheaper check for the most common case when there are no changes
        if len(elements) == len(before):
            has_changes = False
            for i in range(len(before)):
                if before[i].element is not elements[i]:
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
        return self if before is self._before else replace(self, _before=before)

    _element: T

    @property
    def element(self) -> T:
        return self._element

    def with_element(self, element: T) -> JLeftPadded[T]:
        return self if element is self._element else replace(self, _element=element)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> JLeftPadded[T]:
        return self if markers is self._markers else replace(self, _markers=markers)

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
class JContainer(Generic[J2]):
    _before: Space

    @property
    def before(self) -> Space:
        return self._before

    def with_before(self, before: Space) -> JContainer[J2]:
        return self if before is self._before else replace(self, _before=before)

    _elements: List[JRightPadded[J2]]

    @property
    def elements(self) -> List[J2]:
        return JRightPadded.get_elements(self._elements)

    def with_elements(self, elements: List[J2]) -> JContainer[J2]:
        return self.padding.with_elements(JRightPadded.with_elements(self._elements, elements))

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> JContainer[J2]:
        return self if markers is self._markers else replace(self, _markers=markers)

    @dataclass
    class PaddingHelper(Generic[J3]):
        _t: JContainer[J3]

        @property
        def elements(self) -> List[JRightPadded[J3]]:
            return self._t._elements

        def with_elements(self, elements: List[JRightPadded[J3]]) -> JContainer[J3]:
            return self._t if self._t._elements is elements else JContainer(self._t._before, elements, self._t._markers)

    _padding: Optional[weakref.ReferenceType[JContainer.PaddingHelper[J2]]] = None

    @property
    def padding(self) -> JContainer.PaddingHelper[J2]:
        p: Optional[JContainer.PaddingHelper[J2]]
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
            return JContainer(Space.EMPTY, JRightPadded.with_elements([], elements), Markers.EMPTY)
        return before.padding.with_elements(JRightPadded.with_elements(before._elements, elements))

    _EMPTY: Optional[JContainer[J]] = None

    @classmethod
    def empty(cls) -> JContainer[J2]:
        if cls._EMPTY is None:
            cls._EMPTY = JContainer(Space.EMPTY, [], Markers.EMPTY)
        return cls._EMPTY  # type: ignore

    class Location(Enum):
        ANNOTATION_ARGUMENTS = (Space.Location.ANNOTATION_ARGUMENTS, JRightPadded.Location.ANNOTATION_ARGUMENT)
        CASE = (Space.Location.CASE, JRightPadded.Location.CASE)
        CASE_EXPRESSION = (Space.Location.CASE_EXPRESSION, JRightPadded.Location.CASE_EXPRESSION)
        IMPLEMENTS = (Space.Location.IMPLEMENTS, JRightPadded.Location.IMPLEMENTS)
        LANGUAGE_EXTENSION = (Space.Location.LANGUAGE_EXTENSION, JRightPadded.Location.LANGUAGE_EXTENSION)
        METHOD_DECLARATION_PARAMETERS = (
            Space.Location.METHOD_DECLARATION_PARAMETERS, JRightPadded.Location.METHOD_DECLARATION_PARAMETER)
        METHOD_INVOCATION_ARGUMENTS = (
            Space.Location.METHOD_INVOCATION_ARGUMENTS, JRightPadded.Location.METHOD_INVOCATION_ARGUMENT)
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
