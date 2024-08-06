from __future__ import annotations

import extensions
import weakref
from dataclasses import dataclass, replace
from pathlib import Path
from typing import List, Optional, Protocol
from uuid import UUID
from enum import Enum

from .additional_types import *
from ...core import Checksum, FileAttributes, SourceFile, Tree
from ...core.marker.markers import Markers

class J(Tree, Protocol):
    pass

@dataclass(frozen=True, eq=False)
class AnnotatedType(J, Expression, TypeTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> AnnotatedType:
        return self if id is self._id else AnnotatedType(self._id, self._prefix, self._markers, self._annotations, self._type_expression)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> AnnotatedType:
        return self if prefix is self._prefix else AnnotatedType(self._id, self._prefix, self._markers, self._annotations, self._type_expression)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> AnnotatedType:
        return self if markers is self._markers else AnnotatedType(self._id, self._prefix, self._markers, self._annotations, self._type_expression)

    _annotations: List[Annotation]

    @property
    def annotations(self) -> List[Annotation]:
        return self._annotations

    def with_annotations(self, annotations: List[Annotation]) -> AnnotatedType:
        return self if annotations is self._annotations else AnnotatedType(self._id, self._prefix, self._markers, self._annotations, self._type_expression)

    _type_expression: TypeTree

    @property
    def type_expression(self) -> TypeTree:
        return self._type_expression

    def with_type_expression(self, type_expression: TypeTree) -> AnnotatedType:
        return self if type_expression is self._type_expression else AnnotatedType(self._id, self._prefix, self._markers, self._annotations, self._type_expression)

@dataclass(frozen=True, eq=False)
class Annotation(J, Expression):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Annotation:
        return self if id is self._id else Annotation(self._id, self._prefix, self._markers, self._annotation_type, self._arguments)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Annotation:
        return self if prefix is self._prefix else Annotation(self._id, self._prefix, self._markers, self._annotation_type, self._arguments)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Annotation:
        return self if markers is self._markers else Annotation(self._id, self._prefix, self._markers, self._annotation_type, self._arguments)

    _annotation_type: NameTree

    @property
    def annotation_type(self) -> NameTree:
        return self._annotation_type

    def with_annotation_type(self, annotation_type: NameTree) -> Annotation:
        return self if annotation_type is self._annotation_type else Annotation(self._id, self._prefix, self._markers, self._annotation_type, self._arguments)

    _arguments: Optional[JContainer[Expression]]

    @property
    def arguments(self) -> Optional[Expression]:
        return self._arguments.element

    def with_arguments(self, arguments: Optional[Expression]) -> Annotation:
        return self.padding.with_arguments(JContainer[Expression].with_element(self._arguments, arguments))

    @dataclass
    class PaddingHelper:
        _t: Annotation

        @property
        def arguments(self) -> Optional[JContainer[Expression]]:
            return self._t._arguments

        def with_arguments(self, arguments: Optional[JContainer[Expression]]) -> Annotation:
            return self._t if self._t._arguments is arguments else Annotation(self._t.id, self._t.prefix, self._t.markers, self._t.annotation_type, arguments)

    _padding: weakref.ReferenceType[Annotation.PaddingHelper] = None

    @property
    def padding(self) -> Annotation.PaddingHelper:
        p: Annotation.PaddingHelper
        if self._padding is None:
            p = Annotation.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = Annotation.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class ArrayAccess(J, Expression, TypedTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> ArrayAccess:
        return self if id is self._id else ArrayAccess(self._id, self._prefix, self._markers, self._indexed, self._dimension, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> ArrayAccess:
        return self if prefix is self._prefix else ArrayAccess(self._id, self._prefix, self._markers, self._indexed, self._dimension, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> ArrayAccess:
        return self if markers is self._markers else ArrayAccess(self._id, self._prefix, self._markers, self._indexed, self._dimension, self._type)

    _indexed: Expression

    @property
    def indexed(self) -> Expression:
        return self._indexed

    def with_indexed(self, indexed: Expression) -> ArrayAccess:
        return self if indexed is self._indexed else ArrayAccess(self._id, self._prefix, self._markers, self._indexed, self._dimension, self._type)

    _dimension: ArrayDimension

    @property
    def dimension(self) -> ArrayDimension:
        return self._dimension

    def with_dimension(self, dimension: ArrayDimension) -> ArrayAccess:
        return self if dimension is self._dimension else ArrayAccess(self._id, self._prefix, self._markers, self._indexed, self._dimension, self._type)

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> ArrayAccess:
        return self if type is self._type else ArrayAccess(self._id, self._prefix, self._markers, self._indexed, self._dimension, self._type)

@dataclass(frozen=True, eq=False)
class ArrayType(J, TypeTree, Expression):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> ArrayType:
        return self if id is self._id else ArrayType(self._id, self._prefix, self._markers, self._element_type, self._annotations, self._dimension, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> ArrayType:
        return self if prefix is self._prefix else ArrayType(self._id, self._prefix, self._markers, self._element_type, self._annotations, self._dimension, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> ArrayType:
        return self if markers is self._markers else ArrayType(self._id, self._prefix, self._markers, self._element_type, self._annotations, self._dimension, self._type)

    _element_type: TypeTree

    @property
    def element_type(self) -> TypeTree:
        return self._element_type

    def with_element_type(self, element_type: TypeTree) -> ArrayType:
        return self if element_type is self._element_type else ArrayType(self._id, self._prefix, self._markers, self._element_type, self._annotations, self._dimension, self._type)

    _annotations: Optional[List[Annotation]]

    @property
    def annotations(self) -> Optional[List[Annotation]]:
        return self._annotations

    def with_annotations(self, annotations: Optional[List[Annotation]]) -> ArrayType:
        return self if annotations is self._annotations else ArrayType(self._id, self._prefix, self._markers, self._element_type, self._annotations, self._dimension, self._type)

    _dimension: Optional[JLeftPadded[Space]]

    @property
    def dimension(self) -> Optional[JLeftPadded[Space]]:
        return self._dimension

    def with_dimension(self, dimension: Optional[JLeftPadded[Space]]) -> ArrayType:
        return self if dimension is self._dimension else ArrayType(self._id, self._prefix, self._markers, self._element_type, self._annotations, self._dimension, self._type)

    _type: JavaType

    @property
    def type(self) -> JavaType:
        return self._type

    def with_type(self, type: JavaType) -> ArrayType:
        return self if type is self._type else ArrayType(self._id, self._prefix, self._markers, self._element_type, self._annotations, self._dimension, self._type)

@dataclass(frozen=True, eq=False)
class Assert(J, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Assert:
        return self if id is self._id else Assert(self._id, self._prefix, self._markers, self._condition, self._detail)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Assert:
        return self if prefix is self._prefix else Assert(self._id, self._prefix, self._markers, self._condition, self._detail)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Assert:
        return self if markers is self._markers else Assert(self._id, self._prefix, self._markers, self._condition, self._detail)

    _condition: Expression

    @property
    def condition(self) -> Expression:
        return self._condition

    def with_condition(self, condition: Expression) -> Assert:
        return self if condition is self._condition else Assert(self._id, self._prefix, self._markers, self._condition, self._detail)

    _detail: Optional[JLeftPadded[Expression]]

    @property
    def detail(self) -> Optional[JLeftPadded[Expression]]:
        return self._detail

    def with_detail(self, detail: Optional[JLeftPadded[Expression]]) -> Assert:
        return self if detail is self._detail else Assert(self._id, self._prefix, self._markers, self._condition, self._detail)

@dataclass(frozen=True, eq=False)
class Assignment(J, Statement, Expression, TypedTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Assignment:
        return self if id is self._id else Assignment(self._id, self._prefix, self._markers, self._variable, self._assignment, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Assignment:
        return self if prefix is self._prefix else Assignment(self._id, self._prefix, self._markers, self._variable, self._assignment, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Assignment:
        return self if markers is self._markers else Assignment(self._id, self._prefix, self._markers, self._variable, self._assignment, self._type)

    _variable: Expression

    @property
    def variable(self) -> Expression:
        return self._variable

    def with_variable(self, variable: Expression) -> Assignment:
        return self if variable is self._variable else Assignment(self._id, self._prefix, self._markers, self._variable, self._assignment, self._type)

    _assignment: JLeftPadded[Expression]

    @property
    def assignment(self) -> Expression:
        return self._assignment.element

    def with_assignment(self, assignment: Expression) -> Assignment:
        return self.padding.with_assignment(JLeftPadded.with_element(self._assignment, assignment))

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> Assignment:
        return self if type is self._type else Assignment(self._id, self._prefix, self._markers, self._variable, self._assignment, self._type)

    @dataclass
    class PaddingHelper:
        _t: Assignment

        @property
        def assignment(self) -> JLeftPadded[Expression]:
            return self._t._assignment

        def with_assignment(self, assignment: JLeftPadded[Expression]) -> Assignment:
            return self._t if self._t._assignment is assignment else Assignment(self._t.id, self._t.prefix, self._t.markers, self._t.variable, assignment, self._t.type)

    _padding: weakref.ReferenceType[Assignment.PaddingHelper] = None

    @property
    def padding(self) -> Assignment.PaddingHelper:
        p: Assignment.PaddingHelper
        if self._padding is None:
            p = Assignment.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = Assignment.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class AssignmentOperation(J, Statement, Expression, TypedTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> AssignmentOperation:
        return self if id is self._id else AssignmentOperation(self._id, self._prefix, self._markers, self._variable, self._operator, self._assignment, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> AssignmentOperation:
        return self if prefix is self._prefix else AssignmentOperation(self._id, self._prefix, self._markers, self._variable, self._operator, self._assignment, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> AssignmentOperation:
        return self if markers is self._markers else AssignmentOperation(self._id, self._prefix, self._markers, self._variable, self._operator, self._assignment, self._type)

    _variable: Expression

    @property
    def variable(self) -> Expression:
        return self._variable

    def with_variable(self, variable: Expression) -> AssignmentOperation:
        return self if variable is self._variable else AssignmentOperation(self._id, self._prefix, self._markers, self._variable, self._operator, self._assignment, self._type)

    _operator: JLeftPadded[Type]

    @property
    def operator(self) -> AssignmentOperation.Type:
        return self._operator.element

    def with_operator(self, operator: AssignmentOperation.Type) -> AssignmentOperation:
        return self.padding.with_operator(JLeftPadded.with_element(self._operator, operator))

    _assignment: Expression

    @property
    def assignment(self) -> Expression:
        return self._assignment

    def with_assignment(self, assignment: Expression) -> AssignmentOperation:
        return self if assignment is self._assignment else AssignmentOperation(self._id, self._prefix, self._markers, self._variable, self._operator, self._assignment, self._type)

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> AssignmentOperation:
        return self if type is self._type else AssignmentOperation(self._id, self._prefix, self._markers, self._variable, self._operator, self._assignment, self._type)

    class Type(Enum):
        Addition = 0
        BitAnd = 1
        BitOr = 2
        BitXor = 3
        Division = 4
        Exponentiation = 5
        FloorDivision = 6
        LeftShift = 7
        MatrixMultiplication = 8
        Modulo = 9
        Multiplication = 10
        RightShift = 11
        Subtraction = 12
        UnsignedRightShift = 13

    @dataclass
    class PaddingHelper:
        _t: AssignmentOperation

        @property
        def operator(self) -> JLeftPadded[AssignmentOperation.Type]:
            return self._t._operator

        def with_operator(self, operator: JLeftPadded[AssignmentOperation.Type]) -> AssignmentOperation:
            return self._t if self._t._operator is operator else AssignmentOperation(self._t.id, self._t.prefix, self._t.markers, self._t.variable, operator, self._t.assignment, self._t.type)

    _padding: weakref.ReferenceType[AssignmentOperation.PaddingHelper] = None

    @property
    def padding(self) -> AssignmentOperation.PaddingHelper:
        p: AssignmentOperation.PaddingHelper
        if self._padding is None:
            p = AssignmentOperation.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = AssignmentOperation.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class Binary(J, Expression, TypedTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Binary:
        return self if id is self._id else Binary(self._id, self._prefix, self._markers, self._left, self._operator, self._right, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Binary:
        return self if prefix is self._prefix else Binary(self._id, self._prefix, self._markers, self._left, self._operator, self._right, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Binary:
        return self if markers is self._markers else Binary(self._id, self._prefix, self._markers, self._left, self._operator, self._right, self._type)

    _left: Expression

    @property
    def left(self) -> Expression:
        return self._left

    def with_left(self, left: Expression) -> Binary:
        return self if left is self._left else Binary(self._id, self._prefix, self._markers, self._left, self._operator, self._right, self._type)

    _operator: JLeftPadded[Type]

    @property
    def operator(self) -> Binary.Type:
        return self._operator.element

    def with_operator(self, operator: Binary.Type) -> Binary:
        return self.padding.with_operator(JLeftPadded.with_element(self._operator, operator))

    _right: Expression

    @property
    def right(self) -> Expression:
        return self._right

    def with_right(self, right: Expression) -> Binary:
        return self if right is self._right else Binary(self._id, self._prefix, self._markers, self._left, self._operator, self._right, self._type)

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> Binary:
        return self if type is self._type else Binary(self._id, self._prefix, self._markers, self._left, self._operator, self._right, self._type)

    class Type(Enum):
        Addition = 0
        Subtraction = 1
        Multiplication = 2
        Division = 3
        Modulo = 4
        LessThan = 5
        GreaterThan = 6
        LessThanOrEqual = 7
        GreaterThanOrEqual = 8
        Equal = 9
        NotEqual = 10
        BitAnd = 11
        BitOr = 12
        BitXor = 13
        LeftShift = 14
        RightShift = 15
        UnsignedRightShift = 16
        Or = 17
        And = 18

    @dataclass
    class PaddingHelper:
        _t: Binary

        @property
        def operator(self) -> JLeftPadded[Binary.Type]:
            return self._t._operator

        def with_operator(self, operator: JLeftPadded[Binary.Type]) -> Binary:
            return self._t if self._t._operator is operator else Binary(self._t.id, self._t.prefix, self._t.markers, self._t.left, operator, self._t.right, self._t.type)

    _padding: weakref.ReferenceType[Binary.PaddingHelper] = None

    @property
    def padding(self) -> Binary.PaddingHelper:
        p: Binary.PaddingHelper
        if self._padding is None:
            p = Binary.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = Binary.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class Block(J, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Block:
        return self if id is self._id else Block(self._id, self._prefix, self._markers, self._static, self._statements, self._end)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Block:
        return self if prefix is self._prefix else Block(self._id, self._prefix, self._markers, self._static, self._statements, self._end)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Block:
        return self if markers is self._markers else Block(self._id, self._prefix, self._markers, self._static, self._statements, self._end)

    _static: JRightPadded[bool]

    @property
    def static(self) -> bool:
        return self._static.element

    def with_static(self, static: bool) -> Block:
        return self.padding.with_static(JRightPadded.with_element(self._static, static))

    _statements: List[JRightPadded[Statement]]

    @property
    def statements(self) -> List[Statement]:
        return JRightPadded.get_elements(self._statements)

    def with_statements(self, statements: List[Statement]) -> Block:
        return self.padding.with_statements(JRightPadded.with_elements(self._statements, statements))

    _end: Space

    @property
    def end(self) -> Space:
        return self._end

    def with_end(self, end: Space) -> Block:
        return self if end is self._end else Block(self._id, self._prefix, self._markers, self._static, self._statements, self._end)

    @dataclass
    class PaddingHelper:
        _t: Block

        @property
        def static(self) -> JRightPadded[bool]:
            return self._t._static

        def with_static(self, static: JRightPadded[bool]) -> Block:
            return self._t if self._t._static is static else Block(self._t.id, self._t.prefix, self._t.markers, static, self._t._statements, self._t.end)

        @property
        def statements(self) -> List[JRightPadded[Statement]]:
            return self._t._statements

        def with_statements(self, statements: List[JRightPadded[Statement]]) -> Block:
            return self._t if self._t._statements is statements else Block(self._t.id, self._t.prefix, self._t.markers, self._t._static, statements, self._t.end)

    _padding: weakref.ReferenceType[Block.PaddingHelper] = None

    @property
    def padding(self) -> Block.PaddingHelper:
        p: Block.PaddingHelper
        if self._padding is None:
            p = Block.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = Block.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class Break(J, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Break:
        return self if id is self._id else Break(self._id, self._prefix, self._markers, self._label)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Break:
        return self if prefix is self._prefix else Break(self._id, self._prefix, self._markers, self._label)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Break:
        return self if markers is self._markers else Break(self._id, self._prefix, self._markers, self._label)

    _label: Optional[Identifier]

    @property
    def label(self) -> Optional[Identifier]:
        return self._label

    def with_label(self, label: Optional[Identifier]) -> Break:
        return self if label is self._label else Break(self._id, self._prefix, self._markers, self._label)

@dataclass(frozen=True, eq=False)
class Case(J, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Case:
        return self if id is self._id else Case(self._id, self._prefix, self._markers, self._type, self._expressions, self._statements, self._body)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Case:
        return self if prefix is self._prefix else Case(self._id, self._prefix, self._markers, self._type, self._expressions, self._statements, self._body)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Case:
        return self if markers is self._markers else Case(self._id, self._prefix, self._markers, self._type, self._expressions, self._statements, self._body)

    _type: Type

    def with_type(self, type: Type) -> Case:
        return self if type is self._type else Case(self._id, self._prefix, self._markers, self._type, self._expressions, self._statements, self._body)

    _expressions: JContainer[Expression]

    @property
    def expressions(self) -> Expression:
        return self._expressions.element

    def with_expressions(self, expressions: Expression) -> Case:
        return self.padding.with_expressions(JContainer.with_element(self._expressions, expressions))

    _statements: JContainer[Statement]

    @property
    def statements(self) -> Statement:
        return self._statements.element

    def with_statements(self, statements: Statement) -> Case:
        return self.padding.with_statements(JContainer.with_element(self._statements, statements))

    _body: Optional[JRightPadded[J]]

    @property
    def body(self) -> Optional[J]:
        return self._body.element

    def with_body(self, body: Optional[J]) -> Case:
        return self.padding.with_body(JRightPadded[J].with_element(self._body, body))

    class Type(Enum):
        Statement = 0
        Rule = 1

    @dataclass
    class PaddingHelper:
        _t: Case

        @property
        def expressions(self) -> JContainer[Expression]:
            return self._t._expressions

        def with_expressions(self, expressions: JContainer[Expression]) -> Case:
            return self._t if self._t._expressions is expressions else Case(self._t.id, self._t.prefix, self._t.markers, self._t.type, expressions, self._t._statements, self._t._body)

        @property
        def statements(self) -> JContainer[Statement]:
            return self._t._statements

        def with_statements(self, statements: JContainer[Statement]) -> Case:
            return self._t if self._t._statements is statements else Case(self._t.id, self._t.prefix, self._t.markers, self._t.type, self._t._expressions, statements, self._t._body)

        @property
        def body(self) -> Optional[JRightPadded[J]]:
            return self._t._body

        def with_body(self, body: Optional[JRightPadded[J]]) -> Case:
            return self._t if self._t._body is body else Case(self._t.id, self._t.prefix, self._t.markers, self._t.type, self._t._expressions, self._t._statements, body)

    _padding: weakref.ReferenceType[Case.PaddingHelper] = None

    @property
    def padding(self) -> Case.PaddingHelper:
        p: Case.PaddingHelper
        if self._padding is None:
            p = Case.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = Case.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class ClassDeclaration(J, Statement, TypedTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> ClassDeclaration:
        return self if id is self._id else ClassDeclaration(self._id, self._prefix, self._markers, self._leading_annotations, self._modifiers, self._kind, self._name, self._type_parameters, self._primary_constructor, self._extends, self._implements, self._permits, self._body, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> ClassDeclaration:
        return self if prefix is self._prefix else ClassDeclaration(self._id, self._prefix, self._markers, self._leading_annotations, self._modifiers, self._kind, self._name, self._type_parameters, self._primary_constructor, self._extends, self._implements, self._permits, self._body, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> ClassDeclaration:
        return self if markers is self._markers else ClassDeclaration(self._id, self._prefix, self._markers, self._leading_annotations, self._modifiers, self._kind, self._name, self._type_parameters, self._primary_constructor, self._extends, self._implements, self._permits, self._body, self._type)

    _leading_annotations: List[Annotation]

    @property
    def leading_annotations(self) -> List[Annotation]:
        return self._leading_annotations

    def with_leading_annotations(self, leading_annotations: List[Annotation]) -> ClassDeclaration:
        return self if leading_annotations is self._leading_annotations else ClassDeclaration(self._id, self._prefix, self._markers, self._leading_annotations, self._modifiers, self._kind, self._name, self._type_parameters, self._primary_constructor, self._extends, self._implements, self._permits, self._body, self._type)

    _modifiers: List[Modifier]

    @property
    def modifiers(self) -> List[Modifier]:
        return self._modifiers

    def with_modifiers(self, modifiers: List[Modifier]) -> ClassDeclaration:
        return self if modifiers is self._modifiers else ClassDeclaration(self._id, self._prefix, self._markers, self._leading_annotations, self._modifiers, self._kind, self._name, self._type_parameters, self._primary_constructor, self._extends, self._implements, self._permits, self._body, self._type)

    _kind: Kind

    def with_kind(self, kind: Kind) -> ClassDeclaration:
        return self if kind is self._kind else ClassDeclaration(self._id, self._prefix, self._markers, self._leading_annotations, self._modifiers, self._kind, self._name, self._type_parameters, self._primary_constructor, self._extends, self._implements, self._permits, self._body, self._type)

    _name: Identifier

    @property
    def name(self) -> Identifier:
        return self._name

    def with_name(self, name: Identifier) -> ClassDeclaration:
        return self if name is self._name else ClassDeclaration(self._id, self._prefix, self._markers, self._leading_annotations, self._modifiers, self._kind, self._name, self._type_parameters, self._primary_constructor, self._extends, self._implements, self._permits, self._body, self._type)

    _type_parameters: Optional[JContainer[TypeParameter]]

    @property
    def type_parameters(self) -> Optional[TypeParameter]:
        return self._type_parameters.element

    def with_type_parameters(self, type_parameters: Optional[TypeParameter]) -> ClassDeclaration:
        return self.padding.with_type_parameters(JContainer[TypeParameter].with_element(self._type_parameters, type_parameters))

    _primary_constructor: Optional[JContainer[Statement]]

    @property
    def primary_constructor(self) -> Optional[Statement]:
        return self._primary_constructor.element

    def with_primary_constructor(self, primary_constructor: Optional[Statement]) -> ClassDeclaration:
        return self.padding.with_primary_constructor(JContainer[Statement].with_element(self._primary_constructor, primary_constructor))

    _extends: Optional[JLeftPadded[TypeTree]]

    @property
    def extends(self) -> Optional[TypeTree]:
        return self._extends.element

    def with_extends(self, extends: Optional[TypeTree]) -> ClassDeclaration:
        return self.padding.with_extends(JLeftPadded[TypeTree].with_element(self._extends, extends))

    _implements: Optional[JContainer[TypeTree]]

    @property
    def implements(self) -> Optional[TypeTree]:
        return self._implements.element

    def with_implements(self, implements: Optional[TypeTree]) -> ClassDeclaration:
        return self.padding.with_implements(JContainer[TypeTree].with_element(self._implements, implements))

    _permits: Optional[JContainer[TypeTree]]

    @property
    def permits(self) -> Optional[TypeTree]:
        return self._permits.element

    def with_permits(self, permits: Optional[TypeTree]) -> ClassDeclaration:
        return self.padding.with_permits(JContainer[TypeTree].with_element(self._permits, permits))

    _body: Block

    @property
    def body(self) -> Block:
        return self._body

    def with_body(self, body: Block) -> ClassDeclaration:
        return self if body is self._body else ClassDeclaration(self._id, self._prefix, self._markers, self._leading_annotations, self._modifiers, self._kind, self._name, self._type_parameters, self._primary_constructor, self._extends, self._implements, self._permits, self._body, self._type)

    _type: Optional[JavaType.FullyQualified]

    @property
    def type(self) -> Optional[JavaType.FullyQualified]:
        return self._type

    def with_type(self, type: Optional[JavaType.FullyQualified]) -> ClassDeclaration:
        return self if type is self._type else ClassDeclaration(self._id, self._prefix, self._markers, self._leading_annotations, self._modifiers, self._kind, self._name, self._type_parameters, self._primary_constructor, self._extends, self._implements, self._permits, self._body, self._type)

    @dataclass(frozen=True, eq=False)
    class Kind(J):
        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> ClassDeclaration.Kind:
            return self if id is self._id else ClassDeclaration.Kind(self._id, self._prefix, self._markers, self._annotations, self._type)

        _prefix: Space

        @property
        def prefix(self) -> Space:
            return self._prefix

        def with_prefix(self, prefix: Space) -> ClassDeclaration.Kind:
            return self if prefix is self._prefix else ClassDeclaration.Kind(self._id, self._prefix, self._markers, self._annotations, self._type)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> ClassDeclaration.Kind:
            return self if markers is self._markers else ClassDeclaration.Kind(self._id, self._prefix, self._markers, self._annotations, self._type)

        _annotations: List[Annotation]

        @property
        def annotations(self) -> List[Annotation]:
            return self._annotations

        def with_annotations(self, annotations: List[Annotation]) -> ClassDeclaration.Kind:
            return self if annotations is self._annotations else ClassDeclaration.Kind(self._id, self._prefix, self._markers, self._annotations, self._type)

        _type: Type

        @property
        def type(self) -> Type:
            return self._type

        def with_type(self, type: Type) -> ClassDeclaration.Kind:
            return self if type is self._type else ClassDeclaration.Kind(self._id, self._prefix, self._markers, self._annotations, self._type)

        class Type(Enum):
            Class = 0
            Enum = 1
            Interface = 2
            Annotation = 3
            Record = 4
            Value = 5

    @dataclass
    class PaddingHelper:
        _t: ClassDeclaration

        @property
        def kind(self) -> ClassDeclaration.Kind:
            return self._t._kind

        def with_kind(self, kind: ClassDeclaration.Kind) -> ClassDeclaration:
            return self._t if self._t._kind is kind else ClassDeclaration(self._t.id, self._t.prefix, self._t.markers, self._t.leading_annotations, self._t.modifiers, kind, self._t.name, self._t._type_parameters, self._t._primary_constructor, self._t._extends, self._t._implements, self._t._permits, self._t.body, self._t.type)

        @property
        def type_parameters(self) -> Optional[JContainer[TypeParameter]]:
            return self._t._type_parameters

        def with_type_parameters(self, type_parameters: Optional[JContainer[TypeParameter]]) -> ClassDeclaration:
            return self._t if self._t._type_parameters is type_parameters else ClassDeclaration(self._t.id, self._t.prefix, self._t.markers, self._t.leading_annotations, self._t.modifiers, self._t._kind, self._t.name, type_parameters, self._t._primary_constructor, self._t._extends, self._t._implements, self._t._permits, self._t.body, self._t.type)

        @property
        def primary_constructor(self) -> Optional[JContainer[Statement]]:
            return self._t._primary_constructor

        def with_primary_constructor(self, primary_constructor: Optional[JContainer[Statement]]) -> ClassDeclaration:
            return self._t if self._t._primary_constructor is primary_constructor else ClassDeclaration(self._t.id, self._t.prefix, self._t.markers, self._t.leading_annotations, self._t.modifiers, self._t._kind, self._t.name, self._t._type_parameters, primary_constructor, self._t._extends, self._t._implements, self._t._permits, self._t.body, self._t.type)

        @property
        def extends(self) -> Optional[JLeftPadded[TypeTree]]:
            return self._t._extends

        def with_extends(self, extends: Optional[JLeftPadded[TypeTree]]) -> ClassDeclaration:
            return self._t if self._t._extends is extends else ClassDeclaration(self._t.id, self._t.prefix, self._t.markers, self._t.leading_annotations, self._t.modifiers, self._t._kind, self._t.name, self._t._type_parameters, self._t._primary_constructor, extends, self._t._implements, self._t._permits, self._t.body, self._t.type)

        @property
        def implements(self) -> Optional[JContainer[TypeTree]]:
            return self._t._implements

        def with_implements(self, implements: Optional[JContainer[TypeTree]]) -> ClassDeclaration:
            return self._t if self._t._implements is implements else ClassDeclaration(self._t.id, self._t.prefix, self._t.markers, self._t.leading_annotations, self._t.modifiers, self._t._kind, self._t.name, self._t._type_parameters, self._t._primary_constructor, self._t._extends, implements, self._t._permits, self._t.body, self._t.type)

        @property
        def permits(self) -> Optional[JContainer[TypeTree]]:
            return self._t._permits

        def with_permits(self, permits: Optional[JContainer[TypeTree]]) -> ClassDeclaration:
            return self._t if self._t._permits is permits else ClassDeclaration(self._t.id, self._t.prefix, self._t.markers, self._t.leading_annotations, self._t.modifiers, self._t._kind, self._t.name, self._t._type_parameters, self._t._primary_constructor, self._t._extends, self._t._implements, permits, self._t.body, self._t.type)

    _padding: weakref.ReferenceType[ClassDeclaration.PaddingHelper] = None

    @property
    def padding(self) -> ClassDeclaration.PaddingHelper:
        p: ClassDeclaration.PaddingHelper
        if self._padding is None:
            p = ClassDeclaration.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = ClassDeclaration.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class CompilationUnit(J, JavaSourceFile["CompilationUnit"], SourceFile["CompilationUnit"]):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> CompilationUnit:
        return self if id is self._id else CompilationUnit(self._id, self._prefix, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._package_declaration, self._imports, self._classes, self._eof)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> CompilationUnit:
        return self if prefix is self._prefix else CompilationUnit(self._id, self._prefix, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._package_declaration, self._imports, self._classes, self._eof)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> CompilationUnit:
        return self if markers is self._markers else CompilationUnit(self._id, self._prefix, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._package_declaration, self._imports, self._classes, self._eof)

    _source_path: Path

    @property
    def source_path(self) -> Path:
        return self._source_path

    def with_source_path(self, source_path: Path) -> CompilationUnit:
        return self if source_path is self._source_path else CompilationUnit(self._id, self._prefix, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._package_declaration, self._imports, self._classes, self._eof)

    _file_attributes: Optional[FileAttributes]

    @property
    def file_attributes(self) -> Optional[FileAttributes]:
        return self._file_attributes

    def with_file_attributes(self, file_attributes: Optional[FileAttributes]) -> CompilationUnit:
        return self if file_attributes is self._file_attributes else CompilationUnit(self._id, self._prefix, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._package_declaration, self._imports, self._classes, self._eof)

    _charset_name: Optional[str]

    def with_charset_name(self, charset_name: Optional[str]) -> CompilationUnit:
        return self if charset_name is self._charset_name else CompilationUnit(self._id, self._prefix, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._package_declaration, self._imports, self._classes, self._eof)

    _charset_bom_marked: bool

    @property
    def charset_bom_marked(self) -> bool:
        return self._charset_bom_marked

    def with_charset_bom_marked(self, charset_bom_marked: bool) -> CompilationUnit:
        return self if charset_bom_marked is self._charset_bom_marked else CompilationUnit(self._id, self._prefix, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._package_declaration, self._imports, self._classes, self._eof)

    _checksum: Optional[Checksum]

    @property
    def checksum(self) -> Optional[Checksum]:
        return self._checksum

    def with_checksum(self, checksum: Optional[Checksum]) -> CompilationUnit:
        return self if checksum is self._checksum else CompilationUnit(self._id, self._prefix, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._package_declaration, self._imports, self._classes, self._eof)

    _package_declaration: Optional[JRightPadded[Package]]

    @property
    def package_declaration(self) -> Optional[Package]:
        return self._package_declaration.element

    def with_package_declaration(self, package_declaration: Optional[Package]) -> CompilationUnit:
        return self.padding.with_package_declaration(JRightPadded[Package].with_element(self._package_declaration, package_declaration))

    _imports: List[JRightPadded[Import]]

    @property
    def imports(self) -> List[Import]:
        return JRightPadded.get_elements(self._imports)

    def with_imports(self, imports: List[Import]) -> CompilationUnit:
        return self.padding.with_imports(JRightPadded.with_elements(self._imports, imports))

    _classes: List[ClassDeclaration]

    @property
    def classes(self) -> List[ClassDeclaration]:
        return self._classes

    def with_classes(self, classes: List[ClassDeclaration]) -> CompilationUnit:
        return self if classes is self._classes else CompilationUnit(self._id, self._prefix, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._package_declaration, self._imports, self._classes, self._eof)

    _eof: Space

    @property
    def eof(self) -> Space:
        return self._eof

    def with_eof(self, eof: Space) -> CompilationUnit:
        return self if eof is self._eof else CompilationUnit(self._id, self._prefix, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._package_declaration, self._imports, self._classes, self._eof)

    @dataclass
    class PaddingHelper:
        _t: CompilationUnit

        @property
        def package_declaration(self) -> Optional[JRightPadded[Package]]:
            return self._t._package_declaration

        def with_package_declaration(self, package_declaration: Optional[JRightPadded[Package]]) -> CompilationUnit:
            return self._t if self._t._package_declaration is package_declaration else CompilationUnit(self._t.id, self._t.prefix, self._t.markers, self._t.source_path, self._t.file_attributes, self._t.charset_name, self._t.charset_bom_marked, self._t.checksum, package_declaration, self._t._imports, self._t.classes, self._t.eof)

        @property
        def imports(self) -> List[JRightPadded[Import]]:
            return self._t._imports

        def with_imports(self, imports: List[JRightPadded[Import]]) -> CompilationUnit:
            return self._t if self._t._imports is imports else CompilationUnit(self._t.id, self._t.prefix, self._t.markers, self._t.source_path, self._t.file_attributes, self._t.charset_name, self._t.charset_bom_marked, self._t.checksum, self._t._package_declaration, imports, self._t.classes, self._t.eof)

    _padding: weakref.ReferenceType[CompilationUnit.PaddingHelper] = None

    @property
    def padding(self) -> CompilationUnit.PaddingHelper:
        p: CompilationUnit.PaddingHelper
        if self._padding is None:
            p = CompilationUnit.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = CompilationUnit.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class Continue(J, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Continue:
        return self if id is self._id else Continue(self._id, self._prefix, self._markers, self._label)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Continue:
        return self if prefix is self._prefix else Continue(self._id, self._prefix, self._markers, self._label)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Continue:
        return self if markers is self._markers else Continue(self._id, self._prefix, self._markers, self._label)

    _label: Optional[Identifier]

    @property
    def label(self) -> Optional[Identifier]:
        return self._label

    def with_label(self, label: Optional[Identifier]) -> Continue:
        return self if label is self._label else Continue(self._id, self._prefix, self._markers, self._label)

@dataclass(frozen=True, eq=False)
class DoWhileLoop(J, Loop):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> DoWhileLoop:
        return self if id is self._id else DoWhileLoop(self._id, self._prefix, self._markers, self._body, self._while_condition)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> DoWhileLoop:
        return self if prefix is self._prefix else DoWhileLoop(self._id, self._prefix, self._markers, self._body, self._while_condition)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> DoWhileLoop:
        return self if markers is self._markers else DoWhileLoop(self._id, self._prefix, self._markers, self._body, self._while_condition)

    _body: JRightPadded[Statement]

    @property
    def body(self) -> Statement:
        return self._body.element

    def with_body(self, body: Statement) -> DoWhileLoop:
        return self.padding.with_body(JRightPadded.with_element(self._body, body))

    _while_condition: JLeftPadded[J.ControlParentheses[Expression]]

    @property
    def while_condition(self) -> J.ControlParentheses[Expression]:
        return self._while_condition.element

    def with_while_condition(self, while_condition: J.ControlParentheses[Expression]) -> DoWhileLoop:
        return self.padding.with_while_condition(JLeftPadded.with_element(self._while_condition, while_condition))

    @dataclass
    class PaddingHelper:
        _t: DoWhileLoop

        @property
        def body(self) -> JRightPadded[Statement]:
            return self._t._body

        def with_body(self, body: JRightPadded[Statement]) -> DoWhileLoop:
            return self._t if self._t._body is body else DoWhileLoop(self._t.id, self._t.prefix, self._t.markers, body, self._t._while_condition)

        @property
        def while_condition(self) -> JLeftPadded[J.ControlParentheses[Expression]]:
            return self._t._while_condition

        def with_while_condition(self, while_condition: JLeftPadded[J.ControlParentheses[Expression]]) -> DoWhileLoop:
            return self._t if self._t._while_condition is while_condition else DoWhileLoop(self._t.id, self._t.prefix, self._t.markers, self._t._body, while_condition)

    _padding: weakref.ReferenceType[DoWhileLoop.PaddingHelper] = None

    @property
    def padding(self) -> DoWhileLoop.PaddingHelper:
        p: DoWhileLoop.PaddingHelper
        if self._padding is None:
            p = DoWhileLoop.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = DoWhileLoop.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class Empty(J, Statement, Expression, TypeTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Empty:
        return self if id is self._id else Empty(self._id, self._prefix, self._markers)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Empty:
        return self if prefix is self._prefix else Empty(self._id, self._prefix, self._markers)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Empty:
        return self if markers is self._markers else Empty(self._id, self._prefix, self._markers)

@dataclass(frozen=True, eq=False)
class EnumValue(J):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> EnumValue:
        return self if id is self._id else EnumValue(self._id, self._prefix, self._markers, self._annotations, self._name, self._initializer)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> EnumValue:
        return self if prefix is self._prefix else EnumValue(self._id, self._prefix, self._markers, self._annotations, self._name, self._initializer)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> EnumValue:
        return self if markers is self._markers else EnumValue(self._id, self._prefix, self._markers, self._annotations, self._name, self._initializer)

    _annotations: List[Annotation]

    @property
    def annotations(self) -> List[Annotation]:
        return self._annotations

    def with_annotations(self, annotations: List[Annotation]) -> EnumValue:
        return self if annotations is self._annotations else EnumValue(self._id, self._prefix, self._markers, self._annotations, self._name, self._initializer)

    _name: Identifier

    @property
    def name(self) -> Identifier:
        return self._name

    def with_name(self, name: Identifier) -> EnumValue:
        return self if name is self._name else EnumValue(self._id, self._prefix, self._markers, self._annotations, self._name, self._initializer)

    _initializer: Optional[NewClass]

    @property
    def initializer(self) -> Optional[NewClass]:
        return self._initializer

    def with_initializer(self, initializer: Optional[NewClass]) -> EnumValue:
        return self if initializer is self._initializer else EnumValue(self._id, self._prefix, self._markers, self._annotations, self._name, self._initializer)

@dataclass(frozen=True, eq=False)
class EnumValueSet(J, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> EnumValueSet:
        return self if id is self._id else EnumValueSet(self._id, self._prefix, self._markers, self._enums, self._terminated_with_semicolon)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> EnumValueSet:
        return self if prefix is self._prefix else EnumValueSet(self._id, self._prefix, self._markers, self._enums, self._terminated_with_semicolon)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> EnumValueSet:
        return self if markers is self._markers else EnumValueSet(self._id, self._prefix, self._markers, self._enums, self._terminated_with_semicolon)

    _enums: List[JRightPadded[EnumValue]]

    @property
    def enums(self) -> List[EnumValue]:
        return JRightPadded.get_elements(self._enums)

    def with_enums(self, enums: List[EnumValue]) -> EnumValueSet:
        return self.padding.with_enums(JRightPadded.with_elements(self._enums, enums))

    _terminated_with_semicolon: bool

    @property
    def terminated_with_semicolon(self) -> bool:
        return self._terminated_with_semicolon

    def with_terminated_with_semicolon(self, terminated_with_semicolon: bool) -> EnumValueSet:
        return self if terminated_with_semicolon is self._terminated_with_semicolon else EnumValueSet(self._id, self._prefix, self._markers, self._enums, self._terminated_with_semicolon)

    @dataclass
    class PaddingHelper:
        _t: EnumValueSet

        @property
        def enums(self) -> List[JRightPadded[EnumValue]]:
            return self._t._enums

        def with_enums(self, enums: List[JRightPadded[EnumValue]]) -> EnumValueSet:
            return self._t if self._t._enums is enums else EnumValueSet(self._t.id, self._t.prefix, self._t.markers, enums, self._t.terminated_with_semicolon)

    _padding: weakref.ReferenceType[EnumValueSet.PaddingHelper] = None

    @property
    def padding(self) -> EnumValueSet.PaddingHelper:
        p: EnumValueSet.PaddingHelper
        if self._padding is None:
            p = EnumValueSet.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = EnumValueSet.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class FieldAccess(J, TypeTree, Expression, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> FieldAccess:
        return self if id is self._id else FieldAccess(self._id, self._prefix, self._markers, self._target, self._name, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> FieldAccess:
        return self if prefix is self._prefix else FieldAccess(self._id, self._prefix, self._markers, self._target, self._name, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> FieldAccess:
        return self if markers is self._markers else FieldAccess(self._id, self._prefix, self._markers, self._target, self._name, self._type)

    _target: Expression

    @property
    def target(self) -> Expression:
        return self._target

    def with_target(self, target: Expression) -> FieldAccess:
        return self if target is self._target else FieldAccess(self._id, self._prefix, self._markers, self._target, self._name, self._type)

    _name: JLeftPadded[Identifier]

    @property
    def name(self) -> Identifier:
        return self._name.element

    def with_name(self, name: Identifier) -> FieldAccess:
        return self.padding.with_name(JLeftPadded.with_element(self._name, name))

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> FieldAccess:
        return self if type is self._type else FieldAccess(self._id, self._prefix, self._markers, self._target, self._name, self._type)

    @dataclass
    class PaddingHelper:
        _t: FieldAccess

        @property
        def name(self) -> JLeftPadded[Identifier]:
            return self._t._name

        def with_name(self, name: JLeftPadded[Identifier]) -> FieldAccess:
            return self._t if self._t._name is name else FieldAccess(self._t.id, self._t.prefix, self._t.markers, self._t.target, name, self._t.type)

    _padding: weakref.ReferenceType[FieldAccess.PaddingHelper] = None

    @property
    def padding(self) -> FieldAccess.PaddingHelper:
        p: FieldAccess.PaddingHelper
        if self._padding is None:
            p = FieldAccess.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = FieldAccess.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class ForEachLoop(J, Loop):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> ForEachLoop:
        return self if id is self._id else ForEachLoop(self._id, self._prefix, self._markers, self._control, self._body)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> ForEachLoop:
        return self if prefix is self._prefix else ForEachLoop(self._id, self._prefix, self._markers, self._control, self._body)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> ForEachLoop:
        return self if markers is self._markers else ForEachLoop(self._id, self._prefix, self._markers, self._control, self._body)

    _control: Control

    @property
    def control(self) -> Control:
        return self._control

    def with_control(self, control: Control) -> ForEachLoop:
        return self if control is self._control else ForEachLoop(self._id, self._prefix, self._markers, self._control, self._body)

    _body: JRightPadded[Statement]

    @property
    def body(self) -> Statement:
        return self._body.element

    def with_body(self, body: Statement) -> ForEachLoop:
        return self.padding.with_body(JRightPadded.with_element(self._body, body))

    @dataclass(frozen=True, eq=False)
    class Control(J):
        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> ForEachLoop.Control:
            return self if id is self._id else ForEachLoop.Control(self._id, self._prefix, self._markers, self._variable, self._iterable)

        _prefix: Space

        @property
        def prefix(self) -> Space:
            return self._prefix

        def with_prefix(self, prefix: Space) -> ForEachLoop.Control:
            return self if prefix is self._prefix else ForEachLoop.Control(self._id, self._prefix, self._markers, self._variable, self._iterable)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> ForEachLoop.Control:
            return self if markers is self._markers else ForEachLoop.Control(self._id, self._prefix, self._markers, self._variable, self._iterable)

        _variable: JRightPadded[VariableDeclarations]

        @property
        def variable(self) -> VariableDeclarations:
            return self._variable.element

        def with_variable(self, variable: VariableDeclarations) -> ForEachLoop.Control:
            return self.padding.with_variable(JRightPadded.with_element(self._variable, variable))

        _iterable: JRightPadded[Expression]

        @property
        def iterable(self) -> Expression:
            return self._iterable.element

        def with_iterable(self, iterable: Expression) -> ForEachLoop.Control:
            return self.padding.with_iterable(JRightPadded.with_element(self._iterable, iterable))

        @dataclass
        class PaddingHelper:
            _t: ForEachLoop.Control

            @property
            def variable(self) -> JRightPadded[VariableDeclarations]:
                return self._t._variable

            def with_variable(self, variable: JRightPadded[VariableDeclarations]) -> ForEachLoop.Control:
                return self._t if self._t._variable is variable else ForEachLoop.Control(self._t.id, self._t.prefix, self._t.markers, variable, self._t._iterable)

            @property
            def iterable(self) -> JRightPadded[Expression]:
                return self._t._iterable

            def with_iterable(self, iterable: JRightPadded[Expression]) -> ForEachLoop.Control:
                return self._t if self._t._iterable is iterable else ForEachLoop.Control(self._t.id, self._t.prefix, self._t.markers, self._t._variable, iterable)

    _padding: weakref.ReferenceType[Control.PaddingHelper] = None

    @property
    def padding(self) -> Control.PaddingHelper:
        p: ForEachLoop.Control.PaddingHelper
        if self._padding is None:
            p = ForEachLoop.Control.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = ForEachLoop.Control.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    @dataclass
    class PaddingHelper:
        _t: ForEachLoop

        @property
        def body(self) -> JRightPadded[Statement]:
            return self._t._body

        def with_body(self, body: JRightPadded[Statement]) -> ForEachLoop:
            return self._t if self._t._body is body else ForEachLoop(self._t.id, self._t.prefix, self._t.markers, self._t.control, body)

    _padding: weakref.ReferenceType[ForEachLoop.PaddingHelper] = None

    @property
    def padding(self) -> ForEachLoop.PaddingHelper:
        p: ForEachLoop.PaddingHelper
        if self._padding is None:
            p = ForEachLoop.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = ForEachLoop.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class ForLoop(J, Loop):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> ForLoop:
        return self if id is self._id else ForLoop(self._id, self._prefix, self._markers, self._control, self._body)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> ForLoop:
        return self if prefix is self._prefix else ForLoop(self._id, self._prefix, self._markers, self._control, self._body)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> ForLoop:
        return self if markers is self._markers else ForLoop(self._id, self._prefix, self._markers, self._control, self._body)

    _control: Control

    @property
    def control(self) -> Control:
        return self._control

    def with_control(self, control: Control) -> ForLoop:
        return self if control is self._control else ForLoop(self._id, self._prefix, self._markers, self._control, self._body)

    _body: JRightPadded[Statement]

    @property
    def body(self) -> Statement:
        return self._body.element

    def with_body(self, body: Statement) -> ForLoop:
        return self.padding.with_body(JRightPadded.with_element(self._body, body))

    @dataclass(frozen=True, eq=False)
    class Control(J):
        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> ForLoop.Control:
            return self if id is self._id else ForLoop.Control(self._id, self._prefix, self._markers, self._init, self._condition, self._update)

        _prefix: Space

        @property
        def prefix(self) -> Space:
            return self._prefix

        def with_prefix(self, prefix: Space) -> ForLoop.Control:
            return self if prefix is self._prefix else ForLoop.Control(self._id, self._prefix, self._markers, self._init, self._condition, self._update)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> ForLoop.Control:
            return self if markers is self._markers else ForLoop.Control(self._id, self._prefix, self._markers, self._init, self._condition, self._update)

        _init: List[JRightPadded[Statement]]

        @property
        def init(self) -> List[Statement]:
            return JRightPadded.get_elements(self._init)

        def with_init(self, init: List[Statement]) -> ForLoop.Control:
            return self.padding.with_init(JRightPadded.with_elements(self._init, init))

        _condition: JRightPadded[Expression]

        @property
        def condition(self) -> Expression:
            return self._condition.element

        def with_condition(self, condition: Expression) -> ForLoop.Control:
            return self.padding.with_condition(JRightPadded.with_element(self._condition, condition))

        _update: List[JRightPadded[Statement]]

        @property
        def update(self) -> List[Statement]:
            return JRightPadded.get_elements(self._update)

        def with_update(self, update: List[Statement]) -> ForLoop.Control:
            return self.padding.with_update(JRightPadded.with_elements(self._update, update))

        @dataclass
        class PaddingHelper:
            _t: ForLoop.Control

            @property
            def init(self) -> List[JRightPadded[Statement]]:
                return self._t._init

            def with_init(self, init: List[JRightPadded[Statement]]) -> ForLoop.Control:
                return self._t if self._t._init is init else ForLoop.Control(self._t.id, self._t.prefix, self._t.markers, init, self._t._condition, self._t._update)

            @property
            def condition(self) -> JRightPadded[Expression]:
                return self._t._condition

            def with_condition(self, condition: JRightPadded[Expression]) -> ForLoop.Control:
                return self._t if self._t._condition is condition else ForLoop.Control(self._t.id, self._t.prefix, self._t.markers, self._t._init, condition, self._t._update)

            @property
            def update(self) -> List[JRightPadded[Statement]]:
                return self._t._update

            def with_update(self, update: List[JRightPadded[Statement]]) -> ForLoop.Control:
                return self._t if self._t._update is update else ForLoop.Control(self._t.id, self._t.prefix, self._t.markers, self._t._init, self._t._condition, update)

    _padding: weakref.ReferenceType[Control.PaddingHelper] = None

    @property
    def padding(self) -> ForLoop.Control.PaddingHelper:
        p: ForLoop.Control.PaddingHelper
        if self._padding is None:
            p = ForLoop.Control.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = ForLoop.Control.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    @dataclass
    class PaddingHelper:
        _t: ForLoop

        @property
        def body(self) -> JRightPadded[Statement]:
            return self._t._body

        def with_body(self, body: JRightPadded[Statement]) -> ForLoop:
            return self._t if self._t._body is body else ForLoop(self._t.id, self._t.prefix, self._t.markers, self._t.control, body)

    _padding: weakref.ReferenceType[ForLoop.PaddingHelper] = None

    @property
    def padding(self) -> ForLoop.PaddingHelper:
        p: ForLoop.PaddingHelper
        if self._padding is None:
            p = ForLoop.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = ForLoop.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class ParenthesizedTypeTree(J, TypeTree, Expression):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> ParenthesizedTypeTree:
        return self if id is self._id else ParenthesizedTypeTree(self._id, self._prefix, self._markers, self._annotations, self._parenthesized_type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> ParenthesizedTypeTree:
        return self if prefix is self._prefix else ParenthesizedTypeTree(self._id, self._prefix, self._markers, self._annotations, self._parenthesized_type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> ParenthesizedTypeTree:
        return self if markers is self._markers else ParenthesizedTypeTree(self._id, self._prefix, self._markers, self._annotations, self._parenthesized_type)

    _annotations: List[Annotation]

    @property
    def annotations(self) -> List[Annotation]:
        return self._annotations

    def with_annotations(self, annotations: List[Annotation]) -> ParenthesizedTypeTree:
        return self if annotations is self._annotations else ParenthesizedTypeTree(self._id, self._prefix, self._markers, self._annotations, self._parenthesized_type)

    _parenthesized_type: J.Parentheses[TypeTree]

    @property
    def parenthesized_type(self) -> J.Parentheses[TypeTree]:
        return self._parenthesized_type

    def with_parenthesized_type(self, parenthesized_type: J.Parentheses[TypeTree]) -> ParenthesizedTypeTree:
        return self if parenthesized_type is self._parenthesized_type else ParenthesizedTypeTree(self._id, self._prefix, self._markers, self._annotations, self._parenthesized_type)

@dataclass(frozen=True, eq=False)
class Identifier(J, TypeTree, Expression):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Identifier:
        return self if id is self._id else Identifier(self._id, self._prefix, self._markers, self._annotations, self._simple_name, self._type, self._field_type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Identifier:
        return self if prefix is self._prefix else Identifier(self._id, self._prefix, self._markers, self._annotations, self._simple_name, self._type, self._field_type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Identifier:
        return self if markers is self._markers else Identifier(self._id, self._prefix, self._markers, self._annotations, self._simple_name, self._type, self._field_type)

    _annotations: List[Annotation]

    @property
    def annotations(self) -> List[Annotation]:
        return self._annotations

    def with_annotations(self, annotations: List[Annotation]) -> Identifier:
        return self if annotations is self._annotations else Identifier(self._id, self._prefix, self._markers, self._annotations, self._simple_name, self._type, self._field_type)

    _simple_name: str

    @property
    def simple_name(self) -> str:
        return self._simple_name

    def with_simple_name(self, simple_name: str) -> Identifier:
        return self if simple_name is self._simple_name else Identifier(self._id, self._prefix, self._markers, self._annotations, self._simple_name, self._type, self._field_type)

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> Identifier:
        return self if type is self._type else Identifier(self._id, self._prefix, self._markers, self._annotations, self._simple_name, self._type, self._field_type)

    _field_type: Optional[JavaType.Variable]

    @property
    def field_type(self) -> Optional[JavaType.Variable]:
        return self._field_type

    def with_field_type(self, field_type: Optional[JavaType.Variable]) -> Identifier:
        return self if field_type is self._field_type else Identifier(self._id, self._prefix, self._markers, self._annotations, self._simple_name, self._type, self._field_type)

@dataclass(frozen=True, eq=False)
class If(J, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> If:
        return self if id is self._id else If(self._id, self._prefix, self._markers, self._if_condition, self._then_part, self._else_part)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> If:
        return self if prefix is self._prefix else If(self._id, self._prefix, self._markers, self._if_condition, self._then_part, self._else_part)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> If:
        return self if markers is self._markers else If(self._id, self._prefix, self._markers, self._if_condition, self._then_part, self._else_part)

    _if_condition: J.ControlParentheses[Expression]

    @property
    def if_condition(self) -> J.ControlParentheses[Expression]:
        return self._if_condition

    def with_if_condition(self, if_condition: J.ControlParentheses[Expression]) -> If:
        return self if if_condition is self._if_condition else If(self._id, self._prefix, self._markers, self._if_condition, self._then_part, self._else_part)

    _then_part: JRightPadded[Statement]

    @property
    def then_part(self) -> Statement:
        return self._then_part.element

    def with_then_part(self, then_part: Statement) -> If:
        return self.padding.with_then_part(JRightPadded.with_element(self._then_part, then_part))

    _else_part: Optional[Else]

    @property
    def else_part(self) -> Optional[Else]:
        return self._else_part

    def with_else_part(self, else_part: Optional[Else]) -> If:
        return self if else_part is self._else_part else If(self._id, self._prefix, self._markers, self._if_condition, self._then_part, self._else_part)

    @dataclass(frozen=True, eq=False)
    class Else(J):
        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> If.Else:
            return self if id is self._id else If.Else(self._id, self._prefix, self._markers, self._body)

        _prefix: Space

        @property
        def prefix(self) -> Space:
            return self._prefix

        def with_prefix(self, prefix: Space) -> If.Else:
            return self if prefix is self._prefix else If.Else(self._id, self._prefix, self._markers, self._body)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> If.Else:
            return self if markers is self._markers else If.Else(self._id, self._prefix, self._markers, self._body)

        _body: JRightPadded[Statement]

        @property
        def body(self) -> Statement:
            return self._body.element

        def with_body(self, body: Statement) -> If.Else:
            return self.padding.with_body(JRightPadded.with_element(self._body, body))

        @dataclass
        class PaddingHelper:
            _t: If.Else

            @property
            def body(self) -> JRightPadded[Statement]:
                return self._t._body

            def with_body(self, body: JRightPadded[Statement]) -> If.Else:
                return self._t if self._t._body is body else If.Else(self._t.id, self._t.prefix, self._t.markers, body)

    _padding: weakref.ReferenceType[If.Else.PaddingHelper] = None

    @property
    def padding(self) -> If.Else.PaddingHelper:
        p: If.Else.PaddingHelper
        if self._padding is None:
            p = If.Else.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = If.Else.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    @dataclass
    class PaddingHelper:
        _t: If

        @property
        def then_part(self) -> JRightPadded[Statement]:
            return self._t._then_part

        def with_then_part(self, then_part: JRightPadded[Statement]) -> If:
            return self._t if self._t._then_part is then_part else If(self._t.id, self._t.prefix, self._t.markers, self._t.if_condition, then_part, self._t.else_part)

    _padding: weakref.ReferenceType[If.PaddingHelper] = None

    @property
    def padding(self) -> If.PaddingHelper:
        p: If.PaddingHelper
        if self._padding is None:
            p = If.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = If.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class Import(Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Import:
        return self if id is self._id else Import(self._id, self._prefix, self._markers, self._static, self._qualid, self._alias)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Import:
        return self if prefix is self._prefix else Import(self._id, self._prefix, self._markers, self._static, self._qualid, self._alias)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Import:
        return self if markers is self._markers else Import(self._id, self._prefix, self._markers, self._static, self._qualid, self._alias)

    _static: JLeftPadded[bool]

    @property
    def static(self) -> bool:
        return self._static.element

    def with_static(self, static: bool) -> Import:
        return self.padding.with_static(JLeftPadded.with_element(self._static, static))

    _qualid: FieldAccess

    @property
    def qualid(self) -> FieldAccess:
        return self._qualid

    def with_qualid(self, qualid: FieldAccess) -> Import:
        return self if qualid is self._qualid else Import(self._id, self._prefix, self._markers, self._static, self._qualid, self._alias)

    _alias: Optional[JLeftPadded[Identifier]]

    @property
    def alias(self) -> Optional[Identifier]:
        return self._alias.element

    def with_alias(self, alias: Optional[Identifier]) -> Import:
        return self.padding.with_alias(JLeftPadded[Identifier].with_element(self._alias, alias))

    @dataclass
    class PaddingHelper:
        _t: Import

        @property
        def static(self) -> JLeftPadded[bool]:
            return self._t._static

        def with_static(self, static: JLeftPadded[bool]) -> Import:
            return self._t if self._t._static is static else Import(self._t.id, self._t.prefix, self._t.markers, static, self._t.qualid, self._t._alias)

        @property
        def alias(self) -> Optional[JLeftPadded[Identifier]]:
            return self._t._alias

        def with_alias(self, alias: Optional[JLeftPadded[Identifier]]) -> Import:
            return self._t if self._t._alias is alias else Import(self._t.id, self._t.prefix, self._t.markers, self._t._static, self._t.qualid, alias)

    _padding: weakref.ReferenceType[Import.PaddingHelper] = None

    @property
    def padding(self) -> Import.PaddingHelper:
        p: Import.PaddingHelper
        if self._padding is None:
            p = Import.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = Import.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class InstanceOf(J, Expression, TypedTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> InstanceOf:
        return self if id is self._id else InstanceOf(self._id, self._prefix, self._markers, self._expression, self._clazz, self._pattern, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> InstanceOf:
        return self if prefix is self._prefix else InstanceOf(self._id, self._prefix, self._markers, self._expression, self._clazz, self._pattern, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> InstanceOf:
        return self if markers is self._markers else InstanceOf(self._id, self._prefix, self._markers, self._expression, self._clazz, self._pattern, self._type)

    _expression: JRightPadded[Expression]

    @property
    def expression(self) -> Expression:
        return self._expression.element

    def with_expression(self, expression: Expression) -> InstanceOf:
        return self.padding.with_expression(JRightPadded.with_element(self._expression, expression))

    _clazz: J

    @property
    def clazz(self) -> J:
        return self._clazz

    def with_clazz(self, clazz: J) -> InstanceOf:
        return self if clazz is self._clazz else InstanceOf(self._id, self._prefix, self._markers, self._expression, self._clazz, self._pattern, self._type)

    _pattern: Optional[J]

    @property
    def pattern(self) -> Optional[J]:
        return self._pattern

    def with_pattern(self, pattern: Optional[J]) -> InstanceOf:
        return self if pattern is self._pattern else InstanceOf(self._id, self._prefix, self._markers, self._expression, self._clazz, self._pattern, self._type)

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> InstanceOf:
        return self if type is self._type else InstanceOf(self._id, self._prefix, self._markers, self._expression, self._clazz, self._pattern, self._type)

    @dataclass
    class PaddingHelper:
        _t: InstanceOf

        @property
        def expression(self) -> JRightPadded[Expression]:
            return self._t._expression

        def with_expression(self, expression: JRightPadded[Expression]) -> InstanceOf:
            return self._t if self._t._expression is expression else InstanceOf(self._t.id, self._t.prefix, self._t.markers, expression, self._t.clazz, self._t.pattern, self._t.type)

    _padding: weakref.ReferenceType[InstanceOf.PaddingHelper] = None

    @property
    def padding(self) -> InstanceOf.PaddingHelper:
        p: InstanceOf.PaddingHelper
        if self._padding is None:
            p = InstanceOf.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = InstanceOf.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class IntersectionType(J, TypeTree, Expression):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> IntersectionType:
        return self if id is self._id else IntersectionType(self._id, self._prefix, self._markers, self._bounds)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> IntersectionType:
        return self if prefix is self._prefix else IntersectionType(self._id, self._prefix, self._markers, self._bounds)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> IntersectionType:
        return self if markers is self._markers else IntersectionType(self._id, self._prefix, self._markers, self._bounds)

    _bounds: JContainer[TypeTree]

    @property
    def bounds(self) -> TypeTree:
        return self._bounds.element

    def with_bounds(self, bounds: TypeTree) -> IntersectionType:
        return self.padding.with_bounds(JContainer.with_element(self._bounds, bounds))

    @dataclass
    class PaddingHelper:
        _t: IntersectionType

        @property
        def bounds(self) -> JContainer[TypeTree]:
            return self._t._bounds

        def with_bounds(self, bounds: JContainer[TypeTree]) -> IntersectionType:
            return self._t if self._t._bounds is bounds else IntersectionType(self._t.id, self._t.prefix, self._t.markers, bounds)

    _padding: weakref.ReferenceType[IntersectionType.PaddingHelper] = None

    @property
    def padding(self) -> IntersectionType.PaddingHelper:
        p: IntersectionType.PaddingHelper
        if self._padding is None:
            p = IntersectionType.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = IntersectionType.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class Label(J, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Label:
        return self if id is self._id else Label(self._id, self._prefix, self._markers, self._label, self._statement)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Label:
        return self if prefix is self._prefix else Label(self._id, self._prefix, self._markers, self._label, self._statement)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Label:
        return self if markers is self._markers else Label(self._id, self._prefix, self._markers, self._label, self._statement)

    _label: JRightPadded[Identifier]

    @property
    def label(self) -> Identifier:
        return self._label.element

    def with_label(self, label: Identifier) -> Label:
        return self.padding.with_label(JRightPadded.with_element(self._label, label))

    _statement: Statement

    @property
    def statement(self) -> Statement:
        return self._statement

    def with_statement(self, statement: Statement) -> Label:
        return self if statement is self._statement else Label(self._id, self._prefix, self._markers, self._label, self._statement)

    @dataclass
    class PaddingHelper:
        _t: Label

        @property
        def label(self) -> JRightPadded[Identifier]:
            return self._t._label

        def with_label(self, label: JRightPadded[Identifier]) -> Label:
            return self._t if self._t._label is label else Label(self._t.id, self._t.prefix, self._t.markers, label, self._t.statement)

    _padding: weakref.ReferenceType[Label.PaddingHelper] = None

    @property
    def padding(self) -> Label.PaddingHelper:
        p: Label.PaddingHelper
        if self._padding is None:
            p = Label.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = Label.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class Lambda(J, Statement, Expression, TypedTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Lambda:
        return self if id is self._id else Lambda(self._id, self._prefix, self._markers, self._parameters, self._arrow, self._body, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Lambda:
        return self if prefix is self._prefix else Lambda(self._id, self._prefix, self._markers, self._parameters, self._arrow, self._body, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Lambda:
        return self if markers is self._markers else Lambda(self._id, self._prefix, self._markers, self._parameters, self._arrow, self._body, self._type)

    _parameters: Parameters

    @property
    def parameters(self) -> Parameters:
        return self._parameters

    def with_parameters(self, parameters: Parameters) -> Lambda:
        return self if parameters is self._parameters else Lambda(self._id, self._prefix, self._markers, self._parameters, self._arrow, self._body, self._type)

    _arrow: Space

    @property
    def arrow(self) -> Space:
        return self._arrow

    def with_arrow(self, arrow: Space) -> Lambda:
        return self if arrow is self._arrow else Lambda(self._id, self._prefix, self._markers, self._parameters, self._arrow, self._body, self._type)

    _body: J

    @property
    def body(self) -> J:
        return self._body

    def with_body(self, body: J) -> Lambda:
        return self if body is self._body else Lambda(self._id, self._prefix, self._markers, self._parameters, self._arrow, self._body, self._type)

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> Lambda:
        return self if type is self._type else Lambda(self._id, self._prefix, self._markers, self._parameters, self._arrow, self._body, self._type)

    @dataclass(frozen=True, eq=False)
    class Parameters(J):
        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> Lambda.Parameters:
            return self if id is self._id else Lambda.Parameters(self._id, self._prefix, self._markers, self._parenthesized, self._parameters)

        _prefix: Space

        @property
        def prefix(self) -> Space:
            return self._prefix

        def with_prefix(self, prefix: Space) -> Lambda.Parameters:
            return self if prefix is self._prefix else Lambda.Parameters(self._id, self._prefix, self._markers, self._parenthesized, self._parameters)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> Lambda.Parameters:
            return self if markers is self._markers else Lambda.Parameters(self._id, self._prefix, self._markers, self._parenthesized, self._parameters)

        _parenthesized: bool

        @property
        def parenthesized(self) -> bool:
            return self._parenthesized

        def with_parenthesized(self, parenthesized: bool) -> Lambda.Parameters:
            return self if parenthesized is self._parenthesized else Lambda.Parameters(self._id, self._prefix, self._markers, self._parenthesized, self._parameters)

        _parameters: List[JRightPadded[J]]

        @property
        def parameters(self) -> List[J]:
            return JRightPadded.get_elements(self._parameters)

        def with_parameters(self, parameters: List[J]) -> Lambda.Parameters:
            return self.padding.with_parameters(JRightPadded.with_elements(self._parameters, parameters))

        @dataclass
        class PaddingHelper:
            _t: Lambda.Parameters

            @property
            def parameters(self) -> List[JRightPadded[J]]:
                return self._t._parameters

            def with_parameters(self, parameters: List[JRightPadded[J]]) -> Lambda.Parameters:
                return self._t if self._t._parameters is parameters else Lambda.Parameters(self._t.id, self._t.prefix, self._t.markers, self._t.parenthesized, parameters)

    _padding: weakref.ReferenceType[Lambda.Parameters.PaddingHelper] = None

    @property
    def padding(self) -> Lambda.Parameters.PaddingHelper:
        p: Lambda.Parameters.PaddingHelper
        if self._padding is None:
            p = Lambda.Parameters.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = Lambda.Parameters.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class Literal(J, Expression, TypedTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Literal:
        return self if id is self._id else Literal(self._id, self._prefix, self._markers, self._value, self._value_source, self._unicode_escapes, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Literal:
        return self if prefix is self._prefix else Literal(self._id, self._prefix, self._markers, self._value, self._value_source, self._unicode_escapes, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Literal:
        return self if markers is self._markers else Literal(self._id, self._prefix, self._markers, self._value, self._value_source, self._unicode_escapes, self._type)

    _value: Optional[object]

    @property
    def value(self) -> Optional[object]:
        return self._value

    def with_value(self, value: Optional[object]) -> Literal:
        return self if value is self._value else Literal(self._id, self._prefix, self._markers, self._value, self._value_source, self._unicode_escapes, self._type)

    _value_source: Optional[str]

    @property
    def value_source(self) -> Optional[str]:
        return self._value_source

    def with_value_source(self, value_source: Optional[str]) -> Literal:
        return self if value_source is self._value_source else Literal(self._id, self._prefix, self._markers, self._value, self._value_source, self._unicode_escapes, self._type)

    _unicode_escapes: Optional[List[UnicodeEscape]]

    @property
    def unicode_escapes(self) -> Optional[List[UnicodeEscape]]:
        return self._unicode_escapes

    def with_unicode_escapes(self, unicode_escapes: Optional[List[UnicodeEscape]]) -> Literal:
        return self if unicode_escapes is self._unicode_escapes else Literal(self._id, self._prefix, self._markers, self._value, self._value_source, self._unicode_escapes, self._type)

    _type: JavaType.Primitive

    @property
    def type(self) -> JavaType.Primitive:
        return self._type

    def with_type(self, type: JavaType.Primitive) -> Literal:
        return self if type is self._type else Literal(self._id, self._prefix, self._markers, self._value, self._value_source, self._unicode_escapes, self._type)

    @dataclass
    class UnicodeEscape:
        _value_source_index: int

        @property
        def value_source_index(self) -> int:
            return self._value_source_index

        def with_value_source_index(self, value_source_index: int) -> Literal.UnicodeEscape:
            return self if value_source_index is self._value_source_index else Literal.UnicodeEscape(value_source_index, self._code_point)

        _code_point: str

        @property
        def code_point(self) -> str:
            return self._code_point

        def with_code_point(self, code_point: str) -> Literal.UnicodeEscape:
            return self if code_point is self._code_point else Literal.UnicodeEscape(self._value_source_index, code_point)

@dataclass(frozen=True, eq=False)
class MemberReference(J, Expression, TypedTree, MethodCall):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> MemberReference:
        return self if id is self._id else MemberReference(self._id, self._prefix, self._markers, self._containing, self._type_parameters, self._reference, self._type, self._method_type, self._variable_type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> MemberReference:
        return self if prefix is self._prefix else MemberReference(self._id, self._prefix, self._markers, self._containing, self._type_parameters, self._reference, self._type, self._method_type, self._variable_type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> MemberReference:
        return self if markers is self._markers else MemberReference(self._id, self._prefix, self._markers, self._containing, self._type_parameters, self._reference, self._type, self._method_type, self._variable_type)

    _containing: JRightPadded[Expression]

    @property
    def containing(self) -> Expression:
        return self._containing.element

    def with_containing(self, containing: Expression) -> MemberReference:
        return self.padding.with_containing(JRightPadded.with_element(self._containing, containing))

    _type_parameters: Optional[JContainer[Expression]]

    @property
    def type_parameters(self) -> Optional[Expression]:
        return self._type_parameters.element

    def with_type_parameters(self, type_parameters: Optional[Expression]) -> MemberReference:
        return self.padding.with_type_parameters(JContainer[Expression].with_element(self._type_parameters, type_parameters))

    _reference: JLeftPadded[Identifier]

    @property
    def reference(self) -> Identifier:
        return self._reference.element

    def with_reference(self, reference: Identifier) -> MemberReference:
        return self.padding.with_reference(JLeftPadded.with_element(self._reference, reference))

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> MemberReference:
        return self if type is self._type else MemberReference(self._id, self._prefix, self._markers, self._containing, self._type_parameters, self._reference, self._type, self._method_type, self._variable_type)

    _method_type: Optional[JavaType.Method]

    @property
    def method_type(self) -> Optional[JavaType.Method]:
        return self._method_type

    def with_method_type(self, method_type: Optional[JavaType.Method]) -> MemberReference:
        return self if method_type is self._method_type else MemberReference(self._id, self._prefix, self._markers, self._containing, self._type_parameters, self._reference, self._type, self._method_type, self._variable_type)

    _variable_type: Optional[JavaType.Variable]

    @property
    def variable_type(self) -> Optional[JavaType.Variable]:
        return self._variable_type

    def with_variable_type(self, variable_type: Optional[JavaType.Variable]) -> MemberReference:
        return self if variable_type is self._variable_type else MemberReference(self._id, self._prefix, self._markers, self._containing, self._type_parameters, self._reference, self._type, self._method_type, self._variable_type)

    @dataclass
    class PaddingHelper:
        _t: MemberReference

        @property
        def containing(self) -> JRightPadded[Expression]:
            return self._t._containing

        def with_containing(self, containing: JRightPadded[Expression]) -> MemberReference:
            return self._t if self._t._containing is containing else MemberReference(self._t.id, self._t.prefix, self._t.markers, containing, self._t._type_parameters, self._t._reference, self._t.type, self._t.method_type, self._t.variable_type)

        @property
        def type_parameters(self) -> Optional[JContainer[Expression]]:
            return self._t._type_parameters

        def with_type_parameters(self, type_parameters: Optional[JContainer[Expression]]) -> MemberReference:
            return self._t if self._t._type_parameters is type_parameters else MemberReference(self._t.id, self._t.prefix, self._t.markers, self._t._containing, type_parameters, self._t._reference, self._t.type, self._t.method_type, self._t.variable_type)

        @property
        def reference(self) -> JLeftPadded[Identifier]:
            return self._t._reference

        def with_reference(self, reference: JLeftPadded[Identifier]) -> MemberReference:
            return self._t if self._t._reference is reference else MemberReference(self._t.id, self._t.prefix, self._t.markers, self._t._containing, self._t._type_parameters, reference, self._t.type, self._t.method_type, self._t.variable_type)

    _padding: weakref.ReferenceType[MemberReference.PaddingHelper] = None

    @property
    def padding(self) -> MemberReference.PaddingHelper:
        p: MemberReference.PaddingHelper
        if self._padding is None:
            p = MemberReference.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = MemberReference.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class MethodDeclaration(J, Statement, TypedTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> MethodDeclaration:
        return self if id is self._id else MethodDeclaration(self._id, self._prefix, self._markers, self._leading_annotations, self._modifiers, self._type_parameters, self._return_type_expression, self._name, self._parameters, self._throws, self._body, self._default_value, self._method_type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> MethodDeclaration:
        return self if prefix is self._prefix else MethodDeclaration(self._id, self._prefix, self._markers, self._leading_annotations, self._modifiers, self._type_parameters, self._return_type_expression, self._name, self._parameters, self._throws, self._body, self._default_value, self._method_type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> MethodDeclaration:
        return self if markers is self._markers else MethodDeclaration(self._id, self._prefix, self._markers, self._leading_annotations, self._modifiers, self._type_parameters, self._return_type_expression, self._name, self._parameters, self._throws, self._body, self._default_value, self._method_type)

    _leading_annotations: List[Annotation]

    @property
    def leading_annotations(self) -> List[Annotation]:
        return self._leading_annotations

    def with_leading_annotations(self, leading_annotations: List[Annotation]) -> MethodDeclaration:
        return self if leading_annotations is self._leading_annotations else MethodDeclaration(self._id, self._prefix, self._markers, self._leading_annotations, self._modifiers, self._type_parameters, self._return_type_expression, self._name, self._parameters, self._throws, self._body, self._default_value, self._method_type)

    _modifiers: List[Modifier]

    @property
    def modifiers(self) -> List[Modifier]:
        return self._modifiers

    def with_modifiers(self, modifiers: List[Modifier]) -> MethodDeclaration:
        return self if modifiers is self._modifiers else MethodDeclaration(self._id, self._prefix, self._markers, self._leading_annotations, self._modifiers, self._type_parameters, self._return_type_expression, self._name, self._parameters, self._throws, self._body, self._default_value, self._method_type)

    _type_parameters: Optional[TypeParameters]

    _return_type_expression: Optional[TypeTree]

    @property
    def return_type_expression(self) -> Optional[TypeTree]:
        return self._return_type_expression

    def with_return_type_expression(self, return_type_expression: Optional[TypeTree]) -> MethodDeclaration:
        return self if return_type_expression is self._return_type_expression else MethodDeclaration(self._id, self._prefix, self._markers, self._leading_annotations, self._modifiers, self._type_parameters, self._return_type_expression, self._name, self._parameters, self._throws, self._body, self._default_value, self._method_type)

    _name: IdentifierWithAnnotations

    _parameters: JContainer[Statement]

    @property
    def parameters(self) -> Statement:
        return self._parameters.element

    def with_parameters(self, parameters: Statement) -> MethodDeclaration:
        return self.padding.with_parameters(JContainer.with_element(self._parameters, parameters))

    _throws: Optional[JContainer[NameTree]]

    @property
    def throws(self) -> Optional[NameTree]:
        return self._throws.element

    def with_throws(self, throws: Optional[NameTree]) -> MethodDeclaration:
        return self.padding.with_throws(JContainer[NameTree].with_element(self._throws, throws))

    _body: Optional[Block]

    @property
    def body(self) -> Optional[Block]:
        return self._body

    def with_body(self, body: Optional[Block]) -> MethodDeclaration:
        return self if body is self._body else MethodDeclaration(self._id, self._prefix, self._markers, self._leading_annotations, self._modifiers, self._type_parameters, self._return_type_expression, self._name, self._parameters, self._throws, self._body, self._default_value, self._method_type)

    _default_value: Optional[JLeftPadded[Expression]]

    @property
    def default_value(self) -> Optional[Expression]:
        return self._default_value.element

    def with_default_value(self, default_value: Optional[Expression]) -> MethodDeclaration:
        return self.padding.with_default_value(JLeftPadded[Expression].with_element(self._default_value, default_value))

    _method_type: Optional[JavaType.Method]

    @property
    def method_type(self) -> Optional[JavaType.Method]:
        return self._method_type

    def with_method_type(self, method_type: Optional[JavaType.Method]) -> MethodDeclaration:
        return self if method_type is self._method_type else MethodDeclaration(self._id, self._prefix, self._markers, self._leading_annotations, self._modifiers, self._type_parameters, self._return_type_expression, self._name, self._parameters, self._throws, self._body, self._default_value, self._method_type)

    @dataclass
    class IdentifierWithAnnotations:
        _identifier: Identifier

        @property
        def identifier(self) -> Identifier:
            return self._identifier

        def with_identifier(self, identifier: Identifier) -> MethodDeclaration.IdentifierWithAnnotations:
            return self if identifier is self._identifier else MethodDeclaration.IdentifierWithAnnotations(identifier, self._annotations)

        _annotations: List[Annotation]

        @property
        def annotations(self) -> List[Annotation]:
            return self._annotations

        def with_annotations(self, annotations: List[Annotation]) -> MethodDeclaration.IdentifierWithAnnotations:
            return self if annotations is self._annotations else MethodDeclaration.IdentifierWithAnnotations(self._identifier, annotations)

    @dataclass
    class PaddingHelper:
        _t: MethodDeclaration

        @property
        def type_parameters(self) -> Optional[TypeParameters]:
            return self._t._type_parameters

        def with_type_parameters(self, type_parameters: Optional[TypeParameters]) -> MethodDeclaration:
            return self._t if self._t._type_parameters is type_parameters else MethodDeclaration(self._t.id, self._t.prefix, self._t.markers, self._t.leading_annotations, self._t.modifiers, type_parameters, self._t.return_type_expression, self._t._name, self._t._parameters, self._t._throws, self._t.body, self._t._default_value, self._t.method_type)

        @property
        def name(self) -> MethodDeclaration.IdentifierWithAnnotations:
            return self._t._name

        def with_name(self, name: MethodDeclaration.IdentifierWithAnnotations) -> MethodDeclaration:
            return self._t if self._t._name is name else MethodDeclaration(self._t.id, self._t.prefix, self._t.markers, self._t.leading_annotations, self._t.modifiers, self._t._type_parameters, self._t.return_type_expression, name, self._t._parameters, self._t._throws, self._t.body, self._t._default_value, self._t.method_type)

        @property
        def parameters(self) -> JContainer[Statement]:
            return self._t._parameters

        def with_parameters(self, parameters: JContainer[Statement]) -> MethodDeclaration:
            return self._t if self._t._parameters is parameters else MethodDeclaration(self._t.id, self._t.prefix, self._t.markers, self._t.leading_annotations, self._t.modifiers, self._t._type_parameters, self._t.return_type_expression, self._t._name, parameters, self._t._throws, self._t.body, self._t._default_value, self._t.method_type)

        @property
        def throws(self) -> Optional[JContainer[NameTree]]:
            return self._t._throws

        def with_throws(self, throws: Optional[JContainer[NameTree]]) -> MethodDeclaration:
            return self._t if self._t._throws is throws else MethodDeclaration(self._t.id, self._t.prefix, self._t.markers, self._t.leading_annotations, self._t.modifiers, self._t._type_parameters, self._t.return_type_expression, self._t._name, self._t._parameters, throws, self._t.body, self._t._default_value, self._t.method_type)

        @property
        def default_value(self) -> Optional[JLeftPadded[Expression]]:
            return self._t._default_value

        def with_default_value(self, default_value: Optional[JLeftPadded[Expression]]) -> MethodDeclaration:
            return self._t if self._t._default_value is default_value else MethodDeclaration(self._t.id, self._t.prefix, self._t.markers, self._t.leading_annotations, self._t.modifiers, self._t._type_parameters, self._t.return_type_expression, self._t._name, self._t._parameters, self._t._throws, self._t.body, default_value, self._t.method_type)

    @dataclass
    class AnnotationsHelper:
        _t: MethodDeclaration

        @property
        def type_parameters(self) -> Optional[TypeParameters]:
            return self._t._type_parameters

        def with_type_parameters(self, type_parameters: Optional[TypeParameters]) -> MethodDeclaration:
            return self._t if self._t._type_parameters is type_parameters else MethodDeclaration(self._t.id, self._t.prefix, self._t.markers, self._t.leading_annotations, self._t.modifiers, type_parameters, self._t.return_type_expression, self._t._name, self._t._parameters, self._t._throws, self._t.body, self._t._default_value, self._t.method_type)

        @property
        def name(self) -> MethodDeclaration.IdentifierWithAnnotations:
            return self._t._name

        def with_name(self, name: MethodDeclaration.IdentifierWithAnnotations) -> MethodDeclaration:
            return self._t if self._t._name is name else MethodDeclaration(self._t.id, self._t.prefix, self._t.markers, self._t.leading_annotations, self._t.modifiers, self._t._type_parameters, self._t.return_type_expression, name, self._t._parameters, self._t._throws, self._t.body, self._t._default_value, self._t.method_type)

        @property
        def parameters(self) -> JContainer[Statement]:
            return self._t._parameters

        def with_parameters(self, parameters: JContainer[Statement]) -> MethodDeclaration:
            return self._t if self._t._parameters is parameters else MethodDeclaration(self._t.id, self._t.prefix, self._t.markers, self._t.leading_annotations, self._t.modifiers, self._t._type_parameters, self._t.return_type_expression, self._t._name, parameters, self._t._throws, self._t.body, self._t._default_value, self._t.method_type)

        @property
        def throws(self) -> Optional[JContainer[NameTree]]:
            return self._t._throws

        def with_throws(self, throws: Optional[JContainer[NameTree]]) -> MethodDeclaration:
            return self._t if self._t._throws is throws else MethodDeclaration(self._t.id, self._t.prefix, self._t.markers, self._t.leading_annotations, self._t.modifiers, self._t._type_parameters, self._t.return_type_expression, self._t._name, self._t._parameters, throws, self._t.body, self._t._default_value, self._t.method_type)

        @property
        def default_value(self) -> Optional[JLeftPadded[Expression]]:
            return self._t._default_value

        def with_default_value(self, default_value: Optional[JLeftPadded[Expression]]) -> MethodDeclaration:
            return self._t if self._t._default_value is default_value else MethodDeclaration(self._t.id, self._t.prefix, self._t.markers, self._t.leading_annotations, self._t.modifiers, self._t._type_parameters, self._t.return_type_expression, self._t._name, self._t._parameters, self._t._throws, self._t.body, default_value, self._t.method_type)

    _padding: weakref.ReferenceType[MethodDeclaration.PaddingHelper] = None

    @property
    def padding(self) -> MethodDeclaration.PaddingHelper:
        p: MethodDeclaration.PaddingHelper
        if self._padding is None:
            p = MethodDeclaration.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = MethodDeclaration.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    _annotations: weakref.ReferenceType[MethodDeclaration.AnnotationsHelper] = None

    @property
    def padding(self) -> MethodDeclaration.AnnotationsHelper:
        p: MethodDeclaration.AnnotationsHelper
        if self._annotations is None:
            p = MethodDeclaration.AnnotationsHelper(self)
            object.__setattr__(self, '_annotations', weakref.ref(p))
        else:
            p = self._annotations()
            if p is None or p._t != self:
                p = MethodDeclaration.AnnotationsHelper(self)
                object.__setattr__(self, '_annotations', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class MethodInvocation(J, Statement, Expression, TypedTree, MethodCall):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> MethodInvocation:
        return self if id is self._id else MethodInvocation(self._id, self._prefix, self._markers, self._select, self._type_parameters, self._name, self._arguments, self._method_type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> MethodInvocation:
        return self if prefix is self._prefix else MethodInvocation(self._id, self._prefix, self._markers, self._select, self._type_parameters, self._name, self._arguments, self._method_type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> MethodInvocation:
        return self if markers is self._markers else MethodInvocation(self._id, self._prefix, self._markers, self._select, self._type_parameters, self._name, self._arguments, self._method_type)

    _select: Optional[JRightPadded[Expression]]

    @property
    def select(self) -> Optional[Expression]:
        return self._select.element

    def with_select(self, select: Optional[Expression]) -> MethodInvocation:
        return self.padding.with_select(JRightPadded[Expression].with_element(self._select, select))

    _type_parameters: Optional[JContainer[Expression]]

    @property
    def type_parameters(self) -> Optional[Expression]:
        return self._type_parameters.element

    def with_type_parameters(self, type_parameters: Optional[Expression]) -> MethodInvocation:
        return self.padding.with_type_parameters(JContainer[Expression].with_element(self._type_parameters, type_parameters))

    _name: Identifier

    @property
    def name(self) -> Identifier:
        return self._name

    def with_name(self, name: Identifier) -> MethodInvocation:
        return extensions.with_name(self, name)

    _arguments: JContainer[Expression]

    @property
    def arguments(self) -> Expression:
        return self._arguments.element

    def with_arguments(self, arguments: Expression) -> MethodInvocation:
        return self.padding.with_arguments(JContainer.with_element(self._arguments, arguments))

    _method_type: Optional[JavaType.Method]

    @property
    def method_type(self) -> Optional[JavaType.Method]:
        return self._method_type

    def with_method_type(self, method_type: Optional[JavaType.Method]) -> MethodInvocation:
        return self if method_type is self._method_type else MethodInvocation(self._id, self._prefix, self._markers, self._select, self._type_parameters, self._name, self._arguments, self._method_type)

    @dataclass
    class PaddingHelper:
        _t: MethodInvocation

        @property
        def select(self) -> Optional[JRightPadded[Expression]]:
            return self._t._select

        def with_select(self, select: Optional[JRightPadded[Expression]]) -> MethodInvocation:
            return self._t if self._t._select is select else MethodInvocation(self._t.id, self._t.prefix, self._t.markers, select, self._t._type_parameters, self._t.name, self._t._arguments, self._t.method_type)

        @property
        def type_parameters(self) -> Optional[JContainer[Expression]]:
            return self._t._type_parameters

        def with_type_parameters(self, type_parameters: Optional[JContainer[Expression]]) -> MethodInvocation:
            return self._t if self._t._type_parameters is type_parameters else MethodInvocation(self._t.id, self._t.prefix, self._t.markers, self._t._select, type_parameters, self._t.name, self._t._arguments, self._t.method_type)

        @property
        def arguments(self) -> JContainer[Expression]:
            return self._t._arguments

        def with_arguments(self, arguments: JContainer[Expression]) -> MethodInvocation:
            return self._t if self._t._arguments is arguments else MethodInvocation(self._t.id, self._t.prefix, self._t.markers, self._t._select, self._t._type_parameters, self._t.name, arguments, self._t.method_type)

    _padding: weakref.ReferenceType[MethodInvocation.PaddingHelper] = None

    @property
    def padding(self) -> MethodInvocation.PaddingHelper:
        p: MethodInvocation.PaddingHelper
        if self._padding is None:
            p = MethodInvocation.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = MethodInvocation.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class Modifier(J):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Modifier:
        return self if id is self._id else Modifier(self._id, self._prefix, self._markers, self._keyword, self._type, self._annotations)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Modifier:
        return self if prefix is self._prefix else Modifier(self._id, self._prefix, self._markers, self._keyword, self._type, self._annotations)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Modifier:
        return self if markers is self._markers else Modifier(self._id, self._prefix, self._markers, self._keyword, self._type, self._annotations)

    _keyword: Optional[str]

    @property
    def keyword(self) -> Optional[str]:
        return self._keyword

    def with_keyword(self, keyword: Optional[str]) -> Modifier:
        return self if keyword is self._keyword else Modifier(self._id, self._prefix, self._markers, self._keyword, self._type, self._annotations)

    _type: Type

    @property
    def type(self) -> Type:
        return self._type

    def with_type(self, type: Type) -> Modifier:
        return self if type is self._type else Modifier(self._id, self._prefix, self._markers, self._keyword, self._type, self._annotations)

    _annotations: List[Annotation]

    @property
    def annotations(self) -> List[Annotation]:
        return self._annotations

    def with_annotations(self, annotations: List[Annotation]) -> Modifier:
        return self if annotations is self._annotations else Modifier(self._id, self._prefix, self._markers, self._keyword, self._type, self._annotations)

    class Type(Enum):
        Default = 0
        Public = 1
        Protected = 2
        Private = 3
        Abstract = 4
        Static = 5
        Final = 6
        Sealed = 7
        NonSealed = 8
        Transient = 9
        Volatile = 10
        Synchronized = 11
        Native = 12
        Strictfp = 13
        Async = 14
        Reified = 15
        Inline = 16
        LanguageExtension = 17

@dataclass(frozen=True, eq=False)
class MultiCatch(J, TypeTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> MultiCatch:
        return self if id is self._id else MultiCatch(self._id, self._prefix, self._markers, self._alternatives)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> MultiCatch:
        return self if prefix is self._prefix else MultiCatch(self._id, self._prefix, self._markers, self._alternatives)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> MultiCatch:
        return self if markers is self._markers else MultiCatch(self._id, self._prefix, self._markers, self._alternatives)

    _alternatives: List[JRightPadded[NameTree]]

    @property
    def alternatives(self) -> List[NameTree]:
        return JRightPadded.get_elements(self._alternatives)

    def with_alternatives(self, alternatives: List[NameTree]) -> MultiCatch:
        return self.padding.with_alternatives(JRightPadded.with_elements(self._alternatives, alternatives))

    @dataclass
    class PaddingHelper:
        _t: MultiCatch

        @property
        def alternatives(self) -> List[JRightPadded[NameTree]]:
            return self._t._alternatives

        def with_alternatives(self, alternatives: List[JRightPadded[NameTree]]) -> MultiCatch:
            return self._t if self._t._alternatives is alternatives else MultiCatch(self._t.id, self._t.prefix, self._t.markers, alternatives)

    _padding: weakref.ReferenceType[MultiCatch.PaddingHelper] = None

    @property
    def padding(self) -> MultiCatch.PaddingHelper:
        p: MultiCatch.PaddingHelper
        if self._padding is None:
            p = MultiCatch.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = MultiCatch.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class NewArray(J, Expression, TypedTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> NewArray:
        return self if id is self._id else NewArray(self._id, self._prefix, self._markers, self._type_expression, self._dimensions, self._initializer, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> NewArray:
        return self if prefix is self._prefix else NewArray(self._id, self._prefix, self._markers, self._type_expression, self._dimensions, self._initializer, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> NewArray:
        return self if markers is self._markers else NewArray(self._id, self._prefix, self._markers, self._type_expression, self._dimensions, self._initializer, self._type)

    _type_expression: Optional[TypeTree]

    @property
    def type_expression(self) -> Optional[TypeTree]:
        return self._type_expression

    def with_type_expression(self, type_expression: Optional[TypeTree]) -> NewArray:
        return self if type_expression is self._type_expression else NewArray(self._id, self._prefix, self._markers, self._type_expression, self._dimensions, self._initializer, self._type)

    _dimensions: List[ArrayDimension]

    @property
    def dimensions(self) -> List[ArrayDimension]:
        return self._dimensions

    def with_dimensions(self, dimensions: List[ArrayDimension]) -> NewArray:
        return self if dimensions is self._dimensions else NewArray(self._id, self._prefix, self._markers, self._type_expression, self._dimensions, self._initializer, self._type)

    _initializer: Optional[JContainer[Expression]]

    @property
    def initializer(self) -> Optional[Expression]:
        return self._initializer.element

    def with_initializer(self, initializer: Optional[Expression]) -> NewArray:
        return self.padding.with_initializer(JContainer[Expression].with_element(self._initializer, initializer))

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> NewArray:
        return self if type is self._type else NewArray(self._id, self._prefix, self._markers, self._type_expression, self._dimensions, self._initializer, self._type)

    @dataclass
    class PaddingHelper:
        _t: NewArray

        @property
        def initializer(self) -> Optional[JContainer[Expression]]:
            return self._t._initializer

        def with_initializer(self, initializer: Optional[JContainer[Expression]]) -> NewArray:
            return self._t if self._t._initializer is initializer else NewArray(self._t.id, self._t.prefix, self._t.markers, self._t.type_expression, self._t.dimensions, initializer, self._t.type)

    _padding: weakref.ReferenceType[NewArray.PaddingHelper] = None

    @property
    def padding(self) -> NewArray.PaddingHelper:
        p: NewArray.PaddingHelper
        if self._padding is None:
            p = NewArray.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = NewArray.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class ArrayDimension(J):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> ArrayDimension:
        return self if id is self._id else ArrayDimension(self._id, self._prefix, self._markers, self._index)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> ArrayDimension:
        return self if prefix is self._prefix else ArrayDimension(self._id, self._prefix, self._markers, self._index)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> ArrayDimension:
        return self if markers is self._markers else ArrayDimension(self._id, self._prefix, self._markers, self._index)

    _index: JRightPadded[Expression]

    @property
    def index(self) -> Expression:
        return self._index.element

    def with_index(self, index: Expression) -> ArrayDimension:
        return self.padding.with_index(JRightPadded.with_element(self._index, index))

    @dataclass
    class PaddingHelper:
        _t: ArrayDimension

        @property
        def index(self) -> JRightPadded[Expression]:
            return self._t._index

        def with_index(self, index: JRightPadded[Expression]) -> ArrayDimension:
            return self._t if self._t._index is index else ArrayDimension(self._t.id, self._t.prefix, self._t.markers, index)

    _padding: weakref.ReferenceType[ArrayDimension.PaddingHelper] = None

    @property
    def padding(self) -> ArrayDimension.PaddingHelper:
        p: ArrayDimension.PaddingHelper
        if self._padding is None:
            p = ArrayDimension.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = ArrayDimension.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class NewClass(J, Statement, Expression, TypedTree, MethodCall):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> NewClass:
        return self if id is self._id else NewClass(self._id, self._prefix, self._markers, self._enclosing, self._new, self._clazz, self._arguments, self._body, self._constructor_type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> NewClass:
        return self if prefix is self._prefix else NewClass(self._id, self._prefix, self._markers, self._enclosing, self._new, self._clazz, self._arguments, self._body, self._constructor_type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> NewClass:
        return self if markers is self._markers else NewClass(self._id, self._prefix, self._markers, self._enclosing, self._new, self._clazz, self._arguments, self._body, self._constructor_type)

    _enclosing: Optional[JRightPadded[Expression]]

    @property
    def enclosing(self) -> Optional[Expression]:
        return self._enclosing.element

    def with_enclosing(self, enclosing: Optional[Expression]) -> NewClass:
        return self.padding.with_enclosing(JRightPadded[Expression].with_element(self._enclosing, enclosing))

    _new: Space

    @property
    def new(self) -> Space:
        return self._new

    def with_new(self, new: Space) -> NewClass:
        return self if new is self._new else NewClass(self._id, self._prefix, self._markers, self._enclosing, self._new, self._clazz, self._arguments, self._body, self._constructor_type)

    _clazz: Optional[TypeTree]

    @property
    def clazz(self) -> Optional[TypeTree]:
        return self._clazz

    def with_clazz(self, clazz: Optional[TypeTree]) -> NewClass:
        return self if clazz is self._clazz else NewClass(self._id, self._prefix, self._markers, self._enclosing, self._new, self._clazz, self._arguments, self._body, self._constructor_type)

    _arguments: JContainer[Expression]

    @property
    def arguments(self) -> Expression:
        return self._arguments.element

    def with_arguments(self, arguments: Expression) -> NewClass:
        return self.padding.with_arguments(JContainer.with_element(self._arguments, arguments))

    _body: Optional[Block]

    @property
    def body(self) -> Optional[Block]:
        return self._body

    def with_body(self, body: Optional[Block]) -> NewClass:
        return self if body is self._body else NewClass(self._id, self._prefix, self._markers, self._enclosing, self._new, self._clazz, self._arguments, self._body, self._constructor_type)

    _constructor_type: Optional[JavaType.Method]

    @property
    def constructor_type(self) -> Optional[JavaType.Method]:
        return self._constructor_type

    def with_constructor_type(self, constructor_type: Optional[JavaType.Method]) -> NewClass:
        return self if constructor_type is self._constructor_type else NewClass(self._id, self._prefix, self._markers, self._enclosing, self._new, self._clazz, self._arguments, self._body, self._constructor_type)

    @dataclass
    class PaddingHelper:
        _t: NewClass

        @property
        def enclosing(self) -> Optional[JRightPadded[Expression]]:
            return self._t._enclosing

        def with_enclosing(self, enclosing: Optional[JRightPadded[Expression]]) -> NewClass:
            return self._t if self._t._enclosing is enclosing else NewClass(self._t.id, self._t.prefix, self._t.markers, enclosing, self._t.new, self._t.clazz, self._t._arguments, self._t.body, self._t.constructor_type)

        @property
        def arguments(self) -> JContainer[Expression]:
            return self._t._arguments

        def with_arguments(self, arguments: JContainer[Expression]) -> NewClass:
            return self._t if self._t._arguments is arguments else NewClass(self._t.id, self._t.prefix, self._t.markers, self._t._enclosing, self._t.new, self._t.clazz, arguments, self._t.body, self._t.constructor_type)

    _padding: weakref.ReferenceType[NewClass.PaddingHelper] = None

    @property
    def padding(self) -> NewClass.PaddingHelper:
        p: NewClass.PaddingHelper
        if self._padding is None:
            p = NewClass.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = NewClass.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class NullableType(J, TypeTree, Expression):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> NullableType:
        return self if id is self._id else NullableType(self._id, self._prefix, self._markers, self._annotations, self._type_tree)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> NullableType:
        return self if prefix is self._prefix else NullableType(self._id, self._prefix, self._markers, self._annotations, self._type_tree)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> NullableType:
        return self if markers is self._markers else NullableType(self._id, self._prefix, self._markers, self._annotations, self._type_tree)

    _annotations: List[Annotation]

    @property
    def annotations(self) -> List[Annotation]:
        return self._annotations

    def with_annotations(self, annotations: List[Annotation]) -> NullableType:
        return self if annotations is self._annotations else NullableType(self._id, self._prefix, self._markers, self._annotations, self._type_tree)

    _type_tree: JRightPadded[TypeTree]

    @property
    def type_tree(self) -> TypeTree:
        return self._type_tree.element

    def with_type_tree(self, type_tree: TypeTree) -> NullableType:
        return self.padding.with_type_tree(JRightPadded.with_element(self._type_tree, type_tree))

    @dataclass
    class PaddingHelper:
        _t: NullableType

        @property
        def type_tree(self) -> JRightPadded[TypeTree]:
            return self._t._type_tree

        def with_type_tree(self, type_tree: JRightPadded[TypeTree]) -> NullableType:
            return self._t if self._t._type_tree is type_tree else NullableType(self._t.id, self._t.prefix, self._t.markers, self._t.annotations, type_tree)

    _padding: weakref.ReferenceType[NullableType.PaddingHelper] = None

    @property
    def padding(self) -> NullableType.PaddingHelper:
        p: NullableType.PaddingHelper
        if self._padding is None:
            p = NullableType.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = NullableType.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class Package(Statement, J):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Package:
        return self if id is self._id else Package(self._id, self._prefix, self._markers, self._expression, self._annotations)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Package:
        return self if prefix is self._prefix else Package(self._id, self._prefix, self._markers, self._expression, self._annotations)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Package:
        return self if markers is self._markers else Package(self._id, self._prefix, self._markers, self._expression, self._annotations)

    _expression: Expression

    @property
    def expression(self) -> Expression:
        return self._expression

    def with_expression(self, expression: Expression) -> Package:
        return self if expression is self._expression else Package(self._id, self._prefix, self._markers, self._expression, self._annotations)

    _annotations: List[Annotation]

    @property
    def annotations(self) -> List[Annotation]:
        return self._annotations

    def with_annotations(self, annotations: List[Annotation]) -> Package:
        return self if annotations is self._annotations else Package(self._id, self._prefix, self._markers, self._expression, self._annotations)

@dataclass(frozen=True, eq=False)
class ParameterizedType(J, TypeTree, Expression):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> ParameterizedType:
        return self if id is self._id else ParameterizedType(self._id, self._prefix, self._markers, self._clazz, self._type_parameters, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> ParameterizedType:
        return self if prefix is self._prefix else ParameterizedType(self._id, self._prefix, self._markers, self._clazz, self._type_parameters, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> ParameterizedType:
        return self if markers is self._markers else ParameterizedType(self._id, self._prefix, self._markers, self._clazz, self._type_parameters, self._type)

    _clazz: NameTree

    @property
    def clazz(self) -> NameTree:
        return self._clazz

    def with_clazz(self, clazz: NameTree) -> ParameterizedType:
        return self if clazz is self._clazz else ParameterizedType(self._id, self._prefix, self._markers, self._clazz, self._type_parameters, self._type)

    _type_parameters: Optional[JContainer[Expression]]

    @property
    def type_parameters(self) -> Optional[Expression]:
        return self._type_parameters.element

    def with_type_parameters(self, type_parameters: Optional[Expression]) -> ParameterizedType:
        return self.padding.with_type_parameters(JContainer[Expression].with_element(self._type_parameters, type_parameters))

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> ParameterizedType:
        return self if type is self._type else ParameterizedType(self._id, self._prefix, self._markers, self._clazz, self._type_parameters, self._type)

    @dataclass
    class PaddingHelper:
        _t: ParameterizedType

        @property
        def type_parameters(self) -> Optional[JContainer[Expression]]:
            return self._t._type_parameters

        def with_type_parameters(self, type_parameters: Optional[JContainer[Expression]]) -> ParameterizedType:
            return self._t if self._t._type_parameters is type_parameters else ParameterizedType(self._t.id, self._t.prefix, self._t.markers, self._t.clazz, type_parameters, self._t.type)

    _padding: weakref.ReferenceType[ParameterizedType.PaddingHelper] = None

    @property
    def padding(self) -> ParameterizedType.PaddingHelper:
        p: ParameterizedType.PaddingHelper
        if self._padding is None:
            p = ParameterizedType.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = ParameterizedType.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

J2 = TypeVar('J2', bound=J)

@dataclass(frozen=True, eq=False)
class Parentheses(Generic[J2], J, Expression):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Parentheses[J2]:
        return self if id is self._id else Parentheses[J2](self._id, self._prefix, self._markers, self._tree)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Parentheses[J2]:
        return self if prefix is self._prefix else Parentheses[J2](self._id, self._prefix, self._markers, self._tree)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Parentheses[J2]:
        return self if markers is self._markers else Parentheses[J2](self._id, self._prefix, self._markers, self._tree)

    _tree: JRightPadded[J2]

    @property
    def tree(self) -> J2:
        return self._tree.element

    def with_tree(self, tree: J2) -> Parentheses[J2]:
        return self.padding.with_tree(JRightPadded.with_element(self._tree, tree))

    @dataclass
    class PaddingHelper:
        _t: Parentheses[J2]

        @property
        def tree(self) -> JRightPadded[J2]:
            return self._t._tree

        def with_tree(self, tree: JRightPadded[J2]) -> Parentheses[J2]:
            return self._t if self._t._tree is tree else Parentheses[J2](self._t.id, self._t.prefix, self._t.markers, tree)

    _padding: weakref.ReferenceType[Parentheses.PaddingHelper] = None

    @property
    def padding(self) -> Parentheses.PaddingHelper:
        p: Parentheses.PaddingHelper
        if self._padding is None:
            p = Parentheses.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = Parentheses.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class ControlParentheses(J, Expression):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> J.ControlParentheses[J2]:
        return self if id is self._id else J.ControlParentheses[J2](self._id, self._prefix, self._markers, self._tree)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> J.ControlParentheses[J2]:
        return self if prefix is self._prefix else J.ControlParentheses[J2](self._id, self._prefix, self._markers, self._tree)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> J.ControlParentheses[J2]:
        return self if markers is self._markers else J.ControlParentheses[J2](self._id, self._prefix, self._markers, self._tree)

    _tree: JRightPadded[J2]

    @property
    def tree(self) -> J2:
        return self._tree.element

    def with_tree(self, tree: J2) -> J.ControlParentheses[J2]:
        return self.padding.with_tree(JRightPadded.with_element(self._tree, tree))

    @dataclass
    class PaddingHelper:
        _t: J.ControlParentheses[J2]

        @property
        def tree(self) -> JRightPadded[J2]:
            return self._t._tree

        def with_tree(self, tree: JRightPadded[J2]) -> J.ControlParentheses[J2]:
            return self._t if self._t._tree is tree else J.ControlParentheses[J2](self._t.id, self._t.prefix, self._t.markers, tree)

    _padding: weakref.ReferenceType[ControlParentheses.PaddingHelper] = None

    @property
    def padding(self) -> ControlParentheses.PaddingHelper:
        p: ControlParentheses.PaddingHelper
        if self._padding is None:
            p = ControlParentheses.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = ControlParentheses.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class Primitive(J, TypeTree, Expression):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Primitive:
        return self if id is self._id else Primitive(self._id, self._prefix, self._markers, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Primitive:
        return self if prefix is self._prefix else Primitive(self._id, self._prefix, self._markers, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Primitive:
        return self if markers is self._markers else Primitive(self._id, self._prefix, self._markers, self._type)

    _type: JavaType.Primitive

    def with_type(self, type: JavaType.Primitive) -> Primitive:
        return self if type is self._type else Primitive(self._id, self._prefix, self._markers, self._type)

@dataclass(frozen=True, eq=False)
class Return(J, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Return:
        return self if id is self._id else Return(self._id, self._prefix, self._markers, self._expression)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Return:
        return self if prefix is self._prefix else Return(self._id, self._prefix, self._markers, self._expression)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Return:
        return self if markers is self._markers else Return(self._id, self._prefix, self._markers, self._expression)

    _expression: Optional[Expression]

    @property
    def expression(self) -> Optional[Expression]:
        return self._expression

    def with_expression(self, expression: Optional[Expression]) -> Return:
        return self if expression is self._expression else Return(self._id, self._prefix, self._markers, self._expression)

@dataclass(frozen=True, eq=False)
class Switch(J, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Switch:
        return self if id is self._id else Switch(self._id, self._prefix, self._markers, self._selector, self._cases)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Switch:
        return self if prefix is self._prefix else Switch(self._id, self._prefix, self._markers, self._selector, self._cases)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Switch:
        return self if markers is self._markers else Switch(self._id, self._prefix, self._markers, self._selector, self._cases)

    _selector: J.ControlParentheses[Expression]

    @property
    def selector(self) -> J.ControlParentheses[Expression]:
        return self._selector

    def with_selector(self, selector: J.ControlParentheses[Expression]) -> Switch:
        return self if selector is self._selector else Switch(self._id, self._prefix, self._markers, self._selector, self._cases)

    _cases: Block

    @property
    def cases(self) -> Block:
        return self._cases

    def with_cases(self, cases: Block) -> Switch:
        return self if cases is self._cases else Switch(self._id, self._prefix, self._markers, self._selector, self._cases)

@dataclass(frozen=True, eq=False)
class SwitchExpression(J, Expression, TypedTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> SwitchExpression:
        return self if id is self._id else SwitchExpression(self._id, self._prefix, self._markers, self._selector, self._cases)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> SwitchExpression:
        return self if prefix is self._prefix else SwitchExpression(self._id, self._prefix, self._markers, self._selector, self._cases)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> SwitchExpression:
        return self if markers is self._markers else SwitchExpression(self._id, self._prefix, self._markers, self._selector, self._cases)

    _selector: J.ControlParentheses[Expression]

    @property
    def selector(self) -> J.ControlParentheses[Expression]:
        return self._selector

    def with_selector(self, selector: J.ControlParentheses[Expression]) -> SwitchExpression:
        return self if selector is self._selector else SwitchExpression(self._id, self._prefix, self._markers, self._selector, self._cases)

    _cases: Block

    @property
    def cases(self) -> Block:
        return self._cases

    def with_cases(self, cases: Block) -> SwitchExpression:
        return self if cases is self._cases else SwitchExpression(self._id, self._prefix, self._markers, self._selector, self._cases)

@dataclass(frozen=True, eq=False)
class Synchronized(J, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Synchronized:
        return self if id is self._id else Synchronized(self._id, self._prefix, self._markers, self._lock, self._body)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Synchronized:
        return self if prefix is self._prefix else Synchronized(self._id, self._prefix, self._markers, self._lock, self._body)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Synchronized:
        return self if markers is self._markers else Synchronized(self._id, self._prefix, self._markers, self._lock, self._body)

    _lock: J.ControlParentheses[Expression]

    @property
    def lock(self) -> J.ControlParentheses[Expression]:
        return self._lock

    def with_lock(self, lock: J.ControlParentheses[Expression]) -> Synchronized:
        return self if lock is self._lock else Synchronized(self._id, self._prefix, self._markers, self._lock, self._body)

    _body: Block

    @property
    def body(self) -> Block:
        return self._body

    def with_body(self, body: Block) -> Synchronized:
        return self if body is self._body else Synchronized(self._id, self._prefix, self._markers, self._lock, self._body)

@dataclass(frozen=True, eq=False)
class Ternary(J, Expression, Statement, TypedTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Ternary:
        return self if id is self._id else Ternary(self._id, self._prefix, self._markers, self._condition, self._true_part, self._false_part, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Ternary:
        return self if prefix is self._prefix else Ternary(self._id, self._prefix, self._markers, self._condition, self._true_part, self._false_part, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Ternary:
        return self if markers is self._markers else Ternary(self._id, self._prefix, self._markers, self._condition, self._true_part, self._false_part, self._type)

    _condition: Expression

    @property
    def condition(self) -> Expression:
        return self._condition

    def with_condition(self, condition: Expression) -> Ternary:
        return self if condition is self._condition else Ternary(self._id, self._prefix, self._markers, self._condition, self._true_part, self._false_part, self._type)

    _true_part: JLeftPadded[Expression]

    @property
    def true_part(self) -> Expression:
        return self._true_part.element

    def with_true_part(self, true_part: Expression) -> Ternary:
        return self.padding.with_true_part(JLeftPadded.with_element(self._true_part, true_part))

    _false_part: JLeftPadded[Expression]

    @property
    def false_part(self) -> Expression:
        return self._false_part.element

    def with_false_part(self, false_part: Expression) -> Ternary:
        return self.padding.with_false_part(JLeftPadded.with_element(self._false_part, false_part))

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> Ternary:
        return self if type is self._type else Ternary(self._id, self._prefix, self._markers, self._condition, self._true_part, self._false_part, self._type)

    @dataclass
    class PaddingHelper:
        _t: Ternary

        @property
        def true_part(self) -> JLeftPadded[Expression]:
            return self._t._true_part

        def with_true_part(self, true_part: JLeftPadded[Expression]) -> Ternary:
            return self._t if self._t._true_part is true_part else Ternary(self._t.id, self._t.prefix, self._t.markers, self._t.condition, true_part, self._t._false_part, self._t.type)

        @property
        def false_part(self) -> JLeftPadded[Expression]:
            return self._t._false_part

        def with_false_part(self, false_part: JLeftPadded[Expression]) -> Ternary:
            return self._t if self._t._false_part is false_part else Ternary(self._t.id, self._t.prefix, self._t.markers, self._t.condition, self._t._true_part, false_part, self._t.type)

    _padding: weakref.ReferenceType[Ternary.PaddingHelper] = None

    @property
    def padding(self) -> Ternary.PaddingHelper:
        p: Ternary.PaddingHelper
        if self._padding is None:
            p = Ternary.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = Ternary.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class Throw(J, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Throw:
        return self if id is self._id else Throw(self._id, self._prefix, self._markers, self._exception)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Throw:
        return self if prefix is self._prefix else Throw(self._id, self._prefix, self._markers, self._exception)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Throw:
        return self if markers is self._markers else Throw(self._id, self._prefix, self._markers, self._exception)

    _exception: Expression

    @property
    def exception(self) -> Expression:
        return self._exception

    def with_exception(self, exception: Expression) -> Throw:
        return self if exception is self._exception else Throw(self._id, self._prefix, self._markers, self._exception)

@dataclass(frozen=True, eq=False)
class Try(J, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Try:
        return self if id is self._id else Try(self._id, self._prefix, self._markers, self._resources, self._body, self._catches, self._finally)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Try:
        return self if prefix is self._prefix else Try(self._id, self._prefix, self._markers, self._resources, self._body, self._catches, self._finally)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Try:
        return self if markers is self._markers else Try(self._id, self._prefix, self._markers, self._resources, self._body, self._catches, self._finally)

    _resources: Optional[JContainer[Resource]]

    @property
    def resources(self) -> Optional[Try.Resource]:
        return self._resources.element

    def with_resources(self, resources: Optional[Try.Resource]) -> Try:
        return self.padding.with_resources(JContainer[Try.Resource].with_element(self._resources, resources))

    _body: Block

    @property
    def body(self) -> Block:
        return self._body

    def with_body(self, body: Block) -> Try:
        return self if body is self._body else Try(self._id, self._prefix, self._markers, self._resources, self._body, self._catches, self._finally)

    _catches: List[Catch]

    @property
    def catches(self) -> List[Catch]:
        return self._catches

    def with_catches(self, catches: List[Catch]) -> Try:
        return self if catches is self._catches else Try(self._id, self._prefix, self._markers, self._resources, self._body, self._catches, self._finally)

    _finally: Optional[JLeftPadded[Block]]

    @property
    def finally_(self) -> Optional[Block]:
        return self._finally.element

    def with_finally(self, finally_: Optional[Block]) -> Try:
        return self.padding.with_finally(JLeftPadded[Block].with_element(self._finally, finally_))

    @dataclass(frozen=True, eq=False)
    class Resource(J):
        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> Try.Resource:
            return self if id is self._id else Try.Resource(self._id, self._prefix, self._markers, self._variable_declarations, self._terminated_with_semicolon)

        _prefix: Space

        @property
        def prefix(self) -> Space:
            return self._prefix

        def with_prefix(self, prefix: Space) -> Try.Resource:
            return self if prefix is self._prefix else Try.Resource(self._id, self._prefix, self._markers, self._variable_declarations, self._terminated_with_semicolon)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> Try.Resource:
            return self if markers is self._markers else Try.Resource(self._id, self._prefix, self._markers, self._variable_declarations, self._terminated_with_semicolon)

        _variable_declarations: TypedTree

        @property
        def variable_declarations(self) -> TypedTree:
            return self._variable_declarations

        def with_variable_declarations(self, variable_declarations: TypedTree) -> Try.Resource:
            return self if variable_declarations is self._variable_declarations else Try.Resource(self._id, self._prefix, self._markers, self._variable_declarations, self._terminated_with_semicolon)

        _terminated_with_semicolon: bool

        @property
        def terminated_with_semicolon(self) -> bool:
            return self._terminated_with_semicolon

        def with_terminated_with_semicolon(self, terminated_with_semicolon: bool) -> Try.Resource:
            return self if terminated_with_semicolon is self._terminated_with_semicolon else Try.Resource(self._id, self._prefix, self._markers, self._variable_declarations, self._terminated_with_semicolon)

    @dataclass(frozen=True, eq=False)
    class Catch(J):
        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> Try.Catch:
            return self if id is self._id else Try.Catch(self._id, self._prefix, self._markers, self._parameter, self._body)

        _prefix: Space

        @property
        def prefix(self) -> Space:
            return self._prefix

        def with_prefix(self, prefix: Space) -> Try.Catch:
            return self if prefix is self._prefix else Try.Catch(self._id, self._prefix, self._markers, self._parameter, self._body)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> Try.Catch:
            return self if markers is self._markers else Try.Catch(self._id, self._prefix, self._markers, self._parameter, self._body)

        _parameter: J.ControlParentheses[VariableDeclarations]

        @property
        def parameter(self) -> J.ControlParentheses[VariableDeclarations]:
            return self._parameter

        def with_parameter(self, parameter: J.ControlParentheses[VariableDeclarations]) -> Try.Catch:
            return self if parameter is self._parameter else Try.Catch(self._id, self._prefix, self._markers, self._parameter, self._body)

        _body: Block

        @property
        def body(self) -> Block:
            return self._body

        def with_body(self, body: Block) -> Try.Catch:
            return self if body is self._body else Try.Catch(self._id, self._prefix, self._markers, self._parameter, self._body)

    @dataclass
    class PaddingHelper:
        _t: Try

        @property
        def resources(self) -> Optional[JContainer[Try.Resource]]:
            return self._t._resources

        def with_resources(self, resources: Optional[JContainer[Try.Resource]]) -> Try:
            return self._t if self._t._resources is resources else Try(self._t.id, self._t.prefix, self._t.markers, resources, self._t.body, self._t.catches, self._t._finally)

        @property
        def finally_(self) -> Optional[JLeftPadded[Block]]:
            return self._t._finally

        def with_finally(self, finally_: Optional[JLeftPadded[Block]]) -> Try:
            return self._t if self._t._finally is finally_ else Try(self._t.id, self._t.prefix, self._t.markers, self._t._resources, self._t.body, self._t.catches, finally_)

    _padding: weakref.ReferenceType[Try.PaddingHelper] = None

    @property
    def padding(self) -> Try.PaddingHelper:
        p: Try.PaddingHelper
        if self._padding is None:
            p = Try.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = Try.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class TypeCast(J, Expression, TypedTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> TypeCast:
        return self if id is self._id else TypeCast(self._id, self._prefix, self._markers, self._clazz, self._expression)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> TypeCast:
        return self if prefix is self._prefix else TypeCast(self._id, self._prefix, self._markers, self._clazz, self._expression)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> TypeCast:
        return self if markers is self._markers else TypeCast(self._id, self._prefix, self._markers, self._clazz, self._expression)

    _clazz: J.ControlParentheses[TypeTree]

    @property
    def clazz(self) -> J.ControlParentheses[TypeTree]:
        return self._clazz

    def with_clazz(self, clazz: J.ControlParentheses[TypeTree]) -> TypeCast:
        return self if clazz is self._clazz else TypeCast(self._id, self._prefix, self._markers, self._clazz, self._expression)

    _expression: Expression

    @property
    def expression(self) -> Expression:
        return self._expression

    def with_expression(self, expression: Expression) -> TypeCast:
        return self if expression is self._expression else TypeCast(self._id, self._prefix, self._markers, self._clazz, self._expression)

@dataclass(frozen=True, eq=False)
class TypeParameter(J):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> TypeParameter:
        return self if id is self._id else TypeParameter(self._id, self._prefix, self._markers, self._annotations, self._modifiers, self._name, self._bounds)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> TypeParameter:
        return self if prefix is self._prefix else TypeParameter(self._id, self._prefix, self._markers, self._annotations, self._modifiers, self._name, self._bounds)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> TypeParameter:
        return self if markers is self._markers else TypeParameter(self._id, self._prefix, self._markers, self._annotations, self._modifiers, self._name, self._bounds)

    _annotations: List[Annotation]

    @property
    def annotations(self) -> List[Annotation]:
        return self._annotations

    def with_annotations(self, annotations: List[Annotation]) -> TypeParameter:
        return self if annotations is self._annotations else TypeParameter(self._id, self._prefix, self._markers, self._annotations, self._modifiers, self._name, self._bounds)

    _modifiers: List[Modifier]

    @property
    def modifiers(self) -> List[Modifier]:
        return self._modifiers

    def with_modifiers(self, modifiers: List[Modifier]) -> TypeParameter:
        return self if modifiers is self._modifiers else TypeParameter(self._id, self._prefix, self._markers, self._annotations, self._modifiers, self._name, self._bounds)

    _name: Expression

    @property
    def name(self) -> Expression:
        return self._name

    def with_name(self, name: Expression) -> TypeParameter:
        return self if name is self._name else TypeParameter(self._id, self._prefix, self._markers, self._annotations, self._modifiers, self._name, self._bounds)

    _bounds: Optional[JContainer[TypeTree]]

    @property
    def bounds(self) -> Optional[TypeTree]:
        return self._bounds.element

    def with_bounds(self, bounds: Optional[TypeTree]) -> TypeParameter:
        return self.padding.with_bounds(JContainer[TypeTree].with_element(self._bounds, bounds))

    @dataclass
    class PaddingHelper:
        _t: TypeParameter

        @property
        def bounds(self) -> Optional[JContainer[TypeTree]]:
            return self._t._bounds

        def with_bounds(self, bounds: Optional[JContainer[TypeTree]]) -> TypeParameter:
            return self._t if self._t._bounds is bounds else TypeParameter(self._t.id, self._t.prefix, self._t.markers, self._t.annotations, self._t.modifiers, self._t.name, bounds)

    _padding: weakref.ReferenceType[TypeParameter.PaddingHelper] = None

    @property
    def padding(self) -> TypeParameter.PaddingHelper:
        p: TypeParameter.PaddingHelper
        if self._padding is None:
            p = TypeParameter.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = TypeParameter.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class TypeParameters(J):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> TypeParameters:
        return self if id is self._id else TypeParameters(self._id, self._prefix, self._markers, self._annotations, self._type_parameters)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> TypeParameters:
        return self if prefix is self._prefix else TypeParameters(self._id, self._prefix, self._markers, self._annotations, self._type_parameters)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> TypeParameters:
        return self if markers is self._markers else TypeParameters(self._id, self._prefix, self._markers, self._annotations, self._type_parameters)

    _annotations: List[Annotation]

    @property
    def annotations(self) -> List[Annotation]:
        return self._annotations

    def with_annotations(self, annotations: List[Annotation]) -> TypeParameters:
        return self if annotations is self._annotations else TypeParameters(self._id, self._prefix, self._markers, self._annotations, self._type_parameters)

    _type_parameters: List[JRightPadded[TypeParameter]]

    @property
    def type_parameters(self) -> List[TypeParameter]:
        return JRightPadded.get_elements(self._type_parameters)

    def with_type_parameters(self, type_parameters: List[TypeParameter]) -> TypeParameters:
        return self.padding.with_type_parameters(JRightPadded.with_elements(self._type_parameters, type_parameters))

    @dataclass
    class PaddingHelper:
        _t: TypeParameters

        @property
        def type_parameters(self) -> List[JRightPadded[TypeParameter]]:
            return self._t._type_parameters

        def with_type_parameters(self, type_parameters: List[JRightPadded[TypeParameter]]) -> TypeParameters:
            return self._t if self._t._type_parameters is type_parameters else TypeParameters(self._t.id, self._t.prefix, self._t.markers, self._t.annotations, type_parameters)

    _padding: weakref.ReferenceType[TypeParameters.PaddingHelper] = None

    @property
    def padding(self) -> TypeParameters.PaddingHelper:
        p: TypeParameters.PaddingHelper
        if self._padding is None:
            p = TypeParameters.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = TypeParameters.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class Unary(J, Statement, Expression, TypedTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Unary:
        return self if id is self._id else Unary(self._id, self._prefix, self._markers, self._operator, self._expression, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Unary:
        return self if prefix is self._prefix else Unary(self._id, self._prefix, self._markers, self._operator, self._expression, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Unary:
        return self if markers is self._markers else Unary(self._id, self._prefix, self._markers, self._operator, self._expression, self._type)

    _operator: JLeftPadded[Type]

    @property
    def operator(self) -> Unary.Type:
        return self._operator.element

    def with_operator(self, operator: Unary.Type) -> Unary:
        return self.padding.with_operator(JLeftPadded.with_element(self._operator, operator))

    _expression: Expression

    @property
    def expression(self) -> Expression:
        return self._expression

    def with_expression(self, expression: Expression) -> Unary:
        return self if expression is self._expression else Unary(self._id, self._prefix, self._markers, self._operator, self._expression, self._type)

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> Unary:
        return self if type is self._type else Unary(self._id, self._prefix, self._markers, self._operator, self._expression, self._type)

    class Type(Enum):
        PreIncrement = 0
        PreDecrement = 1
        PostIncrement = 2
        PostDecrement = 3
        Positive = 4
        Negative = 5
        Complement = 6
        Not = 7

    @dataclass
    class PaddingHelper:
        _t: Unary

        @property
        def operator(self) -> JLeftPadded[Unary.Type]:
            return self._t._operator

        def with_operator(self, operator: JLeftPadded[Unary.Type]) -> Unary:
            return self._t if self._t._operator is operator else Unary(self._t.id, self._t.prefix, self._t.markers, operator, self._t.expression, self._t.type)

    _padding: weakref.ReferenceType[Unary.PaddingHelper] = None

    @property
    def padding(self) -> Unary.PaddingHelper:
        p: Unary.PaddingHelper
        if self._padding is None:
            p = Unary.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = Unary.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class VariableDeclarations(J, Statement, TypedTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> VariableDeclarations:
        return self if id is self._id else VariableDeclarations(self._id, self._prefix, self._markers, self._leading_annotations, self._modifiers, self._type_expression, self._varargs, self._dimensions_before_name, self._variables)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> VariableDeclarations:
        return self if prefix is self._prefix else VariableDeclarations(self._id, self._prefix, self._markers, self._leading_annotations, self._modifiers, self._type_expression, self._varargs, self._dimensions_before_name, self._variables)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> VariableDeclarations:
        return self if markers is self._markers else VariableDeclarations(self._id, self._prefix, self._markers, self._leading_annotations, self._modifiers, self._type_expression, self._varargs, self._dimensions_before_name, self._variables)

    _leading_annotations: List[Annotation]

    @property
    def leading_annotations(self) -> List[Annotation]:
        return self._leading_annotations

    def with_leading_annotations(self, leading_annotations: List[Annotation]) -> VariableDeclarations:
        return self if leading_annotations is self._leading_annotations else VariableDeclarations(self._id, self._prefix, self._markers, self._leading_annotations, self._modifiers, self._type_expression, self._varargs, self._dimensions_before_name, self._variables)

    _modifiers: List[Modifier]

    @property
    def modifiers(self) -> List[Modifier]:
        return self._modifiers

    def with_modifiers(self, modifiers: List[Modifier]) -> VariableDeclarations:
        return self if modifiers is self._modifiers else VariableDeclarations(self._id, self._prefix, self._markers, self._leading_annotations, self._modifiers, self._type_expression, self._varargs, self._dimensions_before_name, self._variables)

    _type_expression: Optional[TypeTree]

    @property
    def type_expression(self) -> Optional[TypeTree]:
        return self._type_expression

    def with_type_expression(self, type_expression: Optional[TypeTree]) -> VariableDeclarations:
        return self if type_expression is self._type_expression else VariableDeclarations(self._id, self._prefix, self._markers, self._leading_annotations, self._modifiers, self._type_expression, self._varargs, self._dimensions_before_name, self._variables)

    _varargs: Optional[Space]

    @property
    def varargs(self) -> Optional[Space]:
        return self._varargs

    def with_varargs(self, varargs: Optional[Space]) -> VariableDeclarations:
        return self if varargs is self._varargs else VariableDeclarations(self._id, self._prefix, self._markers, self._leading_annotations, self._modifiers, self._type_expression, self._varargs, self._dimensions_before_name, self._variables)

    _dimensions_before_name: List[JLeftPadded[Space]]

    @property
    def dimensions_before_name(self) -> List[JLeftPadded[Space]]:
        return self._dimensions_before_name

    def with_dimensions_before_name(self, dimensions_before_name: List[JLeftPadded[Space]]) -> VariableDeclarations:
        return self if dimensions_before_name is self._dimensions_before_name else VariableDeclarations(self._id, self._prefix, self._markers, self._leading_annotations, self._modifiers, self._type_expression, self._varargs, self._dimensions_before_name, self._variables)

    _variables: List[JRightPadded[NamedVariable]]

    @property
    def variables(self) -> List[VariableDeclarations.NamedVariable]:
        return JRightPadded.get_elements(self._variables)

    def with_variables(self, variables: List[VariableDeclarations.NamedVariable]) -> VariableDeclarations:
        return self.padding.with_variables(JRightPadded.with_elements(self._variables, variables))

    @dataclass(frozen=True, eq=False)
    class NamedVariable(J, NameTree):
        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> VariableDeclarations.NamedVariable:
            return self if id is self._id else VariableDeclarations.NamedVariable(self._id, self._prefix, self._markers, self._name, self._dimensions_after_name, self._initializer, self._variable_type)

        _prefix: Space

        @property
        def prefix(self) -> Space:
            return self._prefix

        def with_prefix(self, prefix: Space) -> VariableDeclarations.NamedVariable:
            return self if prefix is self._prefix else VariableDeclarations.NamedVariable(self._id, self._prefix, self._markers, self._name, self._dimensions_after_name, self._initializer, self._variable_type)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> VariableDeclarations.NamedVariable:
            return self if markers is self._markers else VariableDeclarations.NamedVariable(self._id, self._prefix, self._markers, self._name, self._dimensions_after_name, self._initializer, self._variable_type)

        _name: Identifier

        @property
        def name(self) -> Identifier:
            return self._name

        def with_name(self, name: Identifier) -> VariableDeclarations.NamedVariable:
            return self if name is self._name else VariableDeclarations.NamedVariable(self._id, self._prefix, self._markers, self._name, self._dimensions_after_name, self._initializer, self._variable_type)

        _dimensions_after_name: List[JLeftPadded[Space]]

        @property
        def dimensions_after_name(self) -> List[JLeftPadded[Space]]:
            return self._dimensions_after_name

        def with_dimensions_after_name(self, dimensions_after_name: List[JLeftPadded[Space]]) -> VariableDeclarations.NamedVariable:
            return self if dimensions_after_name is self._dimensions_after_name else VariableDeclarations.NamedVariable(self._id, self._prefix, self._markers, self._name, self._dimensions_after_name, self._initializer, self._variable_type)

        _initializer: Optional[JLeftPadded[Expression]]

        @property
        def initializer(self) -> Optional[Expression]:
            return self._initializer.element

        def with_initializer(self, initializer: Optional[Expression]) -> VariableDeclarations.NamedVariable:
            return self.padding.with_initializer(JLeftPadded[Expression].with_element(self._initializer, initializer))

        _variable_type: Optional[JavaType.Variable]

        @property
        def variable_type(self) -> Optional[JavaType.Variable]:
            return self._variable_type

        def with_variable_type(self, variable_type: Optional[JavaType.Variable]) -> VariableDeclarations.NamedVariable:
            return self if variable_type is self._variable_type else VariableDeclarations.NamedVariable(self._id, self._prefix, self._markers, self._name, self._dimensions_after_name, self._initializer, self._variable_type)

        @dataclass
        class PaddingHelper:
            _t: VariableDeclarations.NamedVariable

            @property
            def initializer(self) -> Optional[JLeftPadded[Expression]]:
                return self._t._initializer

            def with_initializer(self, initializer: Optional[JLeftPadded[Expression]]) -> VariableDeclarations.NamedVariable:
                return self._t if self._t._initializer is initializer else VariableDeclarations.NamedVariable(self._t.id, self._t.prefix, self._t.markers, self._t.name, self._t.dimensions_after_name, initializer, self._t.variable_type)

    _padding: weakref.ReferenceType[NamedVariable.PaddingHelper] = None

    @property
    def padding(self) -> NamedVariable.PaddingHelper:
        p: VariableDeclarations.NamedVariable.PaddingHelper
        if self._padding is None:
            p = VariableDeclarations.NamedVariable.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = VariableDeclarations.NamedVariable.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    @dataclass
    class PaddingHelper:
        _t: VariableDeclarations

        @property
        def variables(self) -> List[JRightPadded[VariableDeclarations.NamedVariable]]:
            return self._t._variables

        def with_variables(self, variables: List[JRightPadded[VariableDeclarations.NamedVariable]]) -> VariableDeclarations:
            return self._t if self._t._variables is variables else VariableDeclarations(self._t.id, self._t.prefix, self._t.markers, self._t.leading_annotations, self._t.modifiers, self._t.type_expression, self._t.varargs, self._t.dimensions_before_name, variables)

    _padding: weakref.ReferenceType[VariableDeclarations.PaddingHelper] = None

    @property
    def padding(self) -> VariableDeclarations.PaddingHelper:
        p: VariableDeclarations.PaddingHelper
        if self._padding is None:
            p = VariableDeclarations.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = VariableDeclarations.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class WhileLoop(J, Loop):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> WhileLoop:
        return self if id is self._id else WhileLoop(self._id, self._prefix, self._markers, self._condition, self._body)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> WhileLoop:
        return self if prefix is self._prefix else WhileLoop(self._id, self._prefix, self._markers, self._condition, self._body)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> WhileLoop:
        return self if markers is self._markers else WhileLoop(self._id, self._prefix, self._markers, self._condition, self._body)

    _condition: J.ControlParentheses[Expression]

    @property
    def condition(self) -> J.ControlParentheses[Expression]:
        return self._condition

    def with_condition(self, condition: J.ControlParentheses[Expression]) -> WhileLoop:
        return self if condition is self._condition else WhileLoop(self._id, self._prefix, self._markers, self._condition, self._body)

    _body: JRightPadded[Statement]

    @property
    def body(self) -> Statement:
        return self._body.element

    def with_body(self, body: Statement) -> WhileLoop:
        return self.padding.with_body(JRightPadded.with_element(self._body, body))

    @dataclass
    class PaddingHelper:
        _t: WhileLoop

        @property
        def body(self) -> JRightPadded[Statement]:
            return self._t._body

        def with_body(self, body: JRightPadded[Statement]) -> WhileLoop:
            return self._t if self._t._body is body else WhileLoop(self._t.id, self._t.prefix, self._t.markers, self._t.condition, body)

    _padding: weakref.ReferenceType[WhileLoop.PaddingHelper] = None

    @property
    def padding(self) -> WhileLoop.PaddingHelper:
        p: WhileLoop.PaddingHelper
        if self._padding is None:
            p = WhileLoop.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = WhileLoop.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class Wildcard(J, Expression, TypeTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Wildcard:
        return self if id is self._id else Wildcard(self._id, self._prefix, self._markers, self._bound, self._bounded_type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Wildcard:
        return self if prefix is self._prefix else Wildcard(self._id, self._prefix, self._markers, self._bound, self._bounded_type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Wildcard:
        return self if markers is self._markers else Wildcard(self._id, self._prefix, self._markers, self._bound, self._bounded_type)

    _bound: Optional[JLeftPadded[Bound]]

    @property
    def bound(self) -> Optional[Wildcard.Bound]:
        return self._bound.element

    def with_bound(self, bound: Optional[Wildcard.Bound]) -> Wildcard:
        return self.padding.with_bound(JLeftPadded[Wildcard.Bound].with_element(self._bound, bound))

    _bounded_type: Optional[NameTree]

    @property
    def bounded_type(self) -> Optional[NameTree]:
        return self._bounded_type

    def with_bounded_type(self, bounded_type: Optional[NameTree]) -> Wildcard:
        return self if bounded_type is self._bounded_type else Wildcard(self._id, self._prefix, self._markers, self._bound, self._bounded_type)

    class Bound(Enum):
        Extends = 0
        Super = 1

    @dataclass
    class PaddingHelper:
        _t: Wildcard

        @property
        def bound(self) -> Optional[JLeftPadded[Wildcard.Bound]]:
            return self._t._bound

        def with_bound(self, bound: Optional[JLeftPadded[Wildcard.Bound]]) -> Wildcard:
            return self._t if self._t._bound is bound else Wildcard(self._t.id, self._t.prefix, self._t.markers, bound, self._t.bounded_type)

    _padding: weakref.ReferenceType[Wildcard.PaddingHelper] = None

    @property
    def padding(self) -> Wildcard.PaddingHelper:
        p: Wildcard.PaddingHelper
        if self._padding is None:
            p = Wildcard.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = Wildcard.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class Yield(J, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Yield:
        return self if id is self._id else Yield(self._id, self._prefix, self._markers, self._implicit, self._value)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Yield:
        return self if prefix is self._prefix else Yield(self._id, self._prefix, self._markers, self._implicit, self._value)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Yield:
        return self if markers is self._markers else Yield(self._id, self._prefix, self._markers, self._implicit, self._value)

    _implicit: bool

    @property
    def implicit(self) -> bool:
        return self._implicit

    def with_implicit(self, implicit: bool) -> Yield:
        return self if implicit is self._implicit else Yield(self._id, self._prefix, self._markers, self._implicit, self._value)

    _value: Expression

    @property
    def value(self) -> Expression:
        return self._value

    def with_value(self, value: Expression) -> Yield:
        return self if value is self._value else Yield(self._id, self._prefix, self._markers, self._implicit, self._value)

@dataclass(frozen=True, eq=False)
class Unknown(J, Statement, Expression, TypeTree, TypedTree, NameTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Unknown:
        return self if id is self._id else Unknown(self._id, self._prefix, self._markers, self._source)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Unknown:
        return self if prefix is self._prefix else Unknown(self._id, self._prefix, self._markers, self._source)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Unknown:
        return self if markers is self._markers else Unknown(self._id, self._prefix, self._markers, self._source)

    _source: Source

    @property
    def source(self) -> Source:
        return self._source

    def with_source(self, source: Source) -> Unknown:
        return self if source is self._source else Unknown(self._id, self._prefix, self._markers, self._source)

    @dataclass(frozen=True, eq=False)
    class Source(J):
        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> Unknown.Source:
            return self if id is self._id else Unknown.Source(self._id, self._prefix, self._markers, self._text)

        _prefix: Space

        @property
        def prefix(self) -> Space:
            return self._prefix

        def with_prefix(self, prefix: Space) -> Unknown.Source:
            return self if prefix is self._prefix else Unknown.Source(self._id, self._prefix, self._markers, self._text)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> Unknown.Source:
            return self if markers is self._markers else Unknown.Source(self._id, self._prefix, self._markers, self._text)

        _text: str

        @property
        def text(self) -> str:
            return self._text

        def with_text(self, text: str) -> Unknown.Source:
            return self if text is self._text else Unknown.Source(self._id, self._prefix, self._markers, self._text)
