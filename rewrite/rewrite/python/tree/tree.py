from __future__ import annotations

import weakref
from dataclasses import dataclass, replace
from pathlib import Path
from typing import List, Optional, Protocol
from uuid import UUID
from enum import Enum

from ...core import Checksum, FileAttributes, SourceFile, Tree
from ...core.marker.markers import Markers
import rewrite.java.tree as j
from ...java.tree.support_types import *
from ...java.tree.tree import Import, Block, Identifier


class Py(Tree, Protocol):
    pass

@dataclass(frozen=True, eq=False)
class ExceptionType(Py, TypeTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> ExceptionType:
        return self if id is self._id else ExceptionType(self._id, self._prefix, self._markers, self._type, self._is_exception_group, self._expression)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> ExceptionType:
        return self if prefix is self._prefix else ExceptionType(self._id, self._prefix, self._markers, self._type, self._is_exception_group, self._expression)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> ExceptionType:
        return self if markers is self._markers else ExceptionType(self._id, self._prefix, self._markers, self._type, self._is_exception_group, self._expression)

    _type: JavaType

    @property
    def type(self) -> JavaType:
        return self._type

    def with_type(self, type: JavaType) -> ExceptionType:
        return self if type is self._type else ExceptionType(self._id, self._prefix, self._markers, self._type, self._is_exception_group, self._expression)

    _is_exception_group: bool

    @property
    def is_exception_group(self) -> bool:
        return self._is_exception_group

    def with_is_exception_group(self, is_exception_group: bool) -> ExceptionType:
        return self if is_exception_group is self._is_exception_group else ExceptionType(self._id, self._prefix, self._markers, self._type, self._is_exception_group, self._expression)

    _expression: Expression

    @property
    def expression(self) -> Expression:
        return self._expression

    def with_expression(self, expression: Expression) -> ExceptionType:
        return self if expression is self._expression else ExceptionType(self._id, self._prefix, self._markers, self._type, self._is_exception_group, self._expression)

@dataclass(frozen=True, eq=False)
class TypeHint(Py, TypeTree):
    class Kind(Enum):
        RETURN_TYPE = 0
        VARIABLE_TYPE = 1

    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> TypeHint:
        return self if id is self._id else TypeHint(self._id, self._prefix, self._markers, self._kind, self._expression, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> TypeHint:
        return self if prefix is self._prefix else TypeHint(self._id, self._prefix, self._markers, self._kind, self._expression, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> TypeHint:
        return self if markers is self._markers else TypeHint(self._id, self._prefix, self._markers, self._kind, self._expression, self._type)

    _kind: Kind

    @property
    def kind(self) -> Kind:
        return self._kind

    def with_kind(self, kind: Kind) -> TypeHint:
        return self if kind is self._kind else TypeHint(self._id, self._prefix, self._markers, self._kind, self._expression, self._type)

    _expression: Expression

    @property
    def expression(self) -> Expression:
        return self._expression

    def with_expression(self, expression: Expression) -> TypeHint:
        return self if expression is self._expression else TypeHint(self._id, self._prefix, self._markers, self._kind, self._expression, self._type)

    _type: JavaType

    @property
    def type(self) -> JavaType:
        return self._type

    def with_type(self, type: JavaType) -> TypeHint:
        return self if type is self._type else TypeHint(self._id, self._prefix, self._markers, self._kind, self._expression, self._type)

@dataclass(frozen=True, eq=False)
class CompilationUnit(Py, JavaSourceFile["CompilationUnit"], SourceFile["CompilationUnit"]):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> CompilationUnit:
        return self if id is self._id else CompilationUnit(self._id, self._prefix, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._imports, self._statements, self._eof)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> CompilationUnit:
        return self if prefix is self._prefix else CompilationUnit(self._id, self._prefix, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._imports, self._statements, self._eof)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> CompilationUnit:
        return self if markers is self._markers else CompilationUnit(self._id, self._prefix, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._imports, self._statements, self._eof)

    _source_path: Path

    @property
    def source_path(self) -> Path:
        return self._source_path

    def with_source_path(self, source_path: Path) -> CompilationUnit:
        return self if source_path is self._source_path else CompilationUnit(self._id, self._prefix, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._imports, self._statements, self._eof)

    _file_attributes: Optional[FileAttributes]

    @property
    def file_attributes(self) -> Optional[FileAttributes]:
        return self._file_attributes

    def with_file_attributes(self, file_attributes: Optional[FileAttributes]) -> CompilationUnit:
        return self if file_attributes is self._file_attributes else CompilationUnit(self._id, self._prefix, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._imports, self._statements, self._eof)

    _charset_name: Optional[str]

    def with_charset_name(self, charset_name: Optional[str]) -> CompilationUnit:
        return self if charset_name is self._charset_name else CompilationUnit(self._id, self._prefix, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._imports, self._statements, self._eof)

    _charset_bom_marked: bool

    @property
    def charset_bom_marked(self) -> bool:
        return self._charset_bom_marked

    def with_charset_bom_marked(self, charset_bom_marked: bool) -> CompilationUnit:
        return self if charset_bom_marked is self._charset_bom_marked else CompilationUnit(self._id, self._prefix, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._imports, self._statements, self._eof)

    _checksum: Optional[Checksum]

    @property
    def checksum(self) -> Optional[Checksum]:
        return self._checksum

    def with_checksum(self, checksum: Optional[Checksum]) -> CompilationUnit:
        return self if checksum is self._checksum else CompilationUnit(self._id, self._prefix, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._imports, self._statements, self._eof)

    _imports: List[JRightPadded[Import]]

    @property
    def imports(self) -> List[Import]:
        return JRightPadded.get_elements(self._imports)

    def with_imports(self, imports: List[Import]) -> CompilationUnit:
        return self.padding.with_imports(JRightPadded.with_elements(self._imports, imports))

    _statements: List[JRightPadded[Statement]]

    @property
    def statements(self) -> List[Statement]:
        return JRightPadded.get_elements(self._statements)

    def with_statements(self, statements: List[Statement]) -> CompilationUnit:
        return self.padding.with_statements(JRightPadded.with_elements(self._statements, statements))

    _eof: Space

    @property
    def eof(self) -> Space:
        return self._eof

    def with_eof(self, eof: Space) -> CompilationUnit:
        return self if eof is self._eof else CompilationUnit(self._id, self._prefix, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._imports, self._statements, self._eof)

    @dataclass
    class PaddingHelper:
        _t: CompilationUnit

        @property
        def imports(self) -> List[JRightPadded[Import]]:
            return self._t._imports

        def with_imports(self, imports: List[JRightPadded[Import]]) -> CompilationUnit:
            return self._t if self._t._imports is imports else CompilationUnit(self._t.id, self._t.prefix, self._t.markers, self._t.source_path, self._t.file_attributes, self._t.charset_name, self._t.charset_bom_marked, self._t.checksum, imports, self._t._statements, self._t.eof)

        @property
        def statements(self) -> List[JRightPadded[Statement]]:
            return self._t._statements

        def with_statements(self, statements: List[JRightPadded[Statement]]) -> CompilationUnit:
            return self._t if self._t._statements is statements else CompilationUnit(self._t.id, self._t.prefix, self._t.markers, self._t.source_path, self._t.file_attributes, self._t.charset_name, self._t.charset_bom_marked, self._t.checksum, self._t._imports, statements, self._t.eof)

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
class ExpressionStatement(Py, Expression, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> ExpressionStatement:
        return self if id is self._id else ExpressionStatement(self._id, self._expression)

    _expression: Expression

    @property
    def expression(self) -> Expression:
        return self._expression

    def with_expression(self, expression: Expression) -> ExpressionStatement:
        return self if expression is self._expression else ExpressionStatement(self._id, self._expression)

@dataclass(frozen=True, eq=False)
class KeyValue(Py, Expression, TypedTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> KeyValue:
        return self if id is self._id else KeyValue(self._id, self._prefix, self._markers, self._key, self._value, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> KeyValue:
        return self if prefix is self._prefix else KeyValue(self._id, self._prefix, self._markers, self._key, self._value, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> KeyValue:
        return self if markers is self._markers else KeyValue(self._id, self._prefix, self._markers, self._key, self._value, self._type)

    _key: JRightPadded[Expression]

    @property
    def key(self) -> Expression:
        return self._key.element

    def with_key(self, key: Expression) -> KeyValue:
        return self.padding.with_key(JRightPadded.with_element(self._key, key))

    _value: Expression

    @property
    def value(self) -> Expression:
        return self._value

    def with_value(self, value: Expression) -> KeyValue:
        return self if value is self._value else KeyValue(self._id, self._prefix, self._markers, self._key, self._value, self._type)

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> KeyValue:
        return self if type is self._type else KeyValue(self._id, self._prefix, self._markers, self._key, self._value, self._type)

    @dataclass
    class PaddingHelper:
        _t: KeyValue

        @property
        def key(self) -> JRightPadded[Expression]:
            return self._t._key

        def with_key(self, key: JRightPadded[Expression]) -> KeyValue:
            return self._t if self._t._key is key else KeyValue(self._t.id, self._t.prefix, self._t.markers, key, self._t.value, self._t.type)

    _padding: weakref.ReferenceType[KeyValue.PaddingHelper] = None

    @property
    def padding(self) -> KeyValue.PaddingHelper:
        p: KeyValue.PaddingHelper
        if self._padding is None:
            p = KeyValue.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = KeyValue.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class DictLiteral(Py, Expression, TypedTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> DictLiteral:
        return self if id is self._id else DictLiteral(self._id, self._prefix, self._markers, self._elements, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> DictLiteral:
        return self if prefix is self._prefix else DictLiteral(self._id, self._prefix, self._markers, self._elements, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> DictLiteral:
        return self if markers is self._markers else DictLiteral(self._id, self._prefix, self._markers, self._elements, self._type)

    _elements: JContainer[KeyValue]

    @property
    def elements(self) -> KeyValue:
        return self._elements.element

    def with_elements(self, elements: KeyValue) -> DictLiteral:
        return self.padding.with_elements(JContainer.with_element(self._elements, elements))

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> DictLiteral:
        return self if type is self._type else DictLiteral(self._id, self._prefix, self._markers, self._elements, self._type)

    @dataclass
    class PaddingHelper:
        _t: DictLiteral

        @property
        def elements(self) -> JContainer[KeyValue]:
            return self._t._elements

        def with_elements(self, elements: JContainer[KeyValue]) -> DictLiteral:
            return self._t if self._t._elements is elements else DictLiteral(self._t.id, self._t.prefix, self._t.markers, elements, self._t.type)

    _padding: weakref.ReferenceType[DictLiteral.PaddingHelper] = None

    @property
    def padding(self) -> DictLiteral.PaddingHelper:
        p: DictLiteral.PaddingHelper
        if self._padding is None:
            p = DictLiteral.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = DictLiteral.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class PassStatement(Py, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> PassStatement:
        return self if id is self._id else PassStatement(self._id, self._prefix, self._markers)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> PassStatement:
        return self if prefix is self._prefix else PassStatement(self._id, self._prefix, self._markers)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> PassStatement:
        return self if markers is self._markers else PassStatement(self._id, self._prefix, self._markers)

@dataclass(frozen=True, eq=False)
class TrailingElseWrapper(Py, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> TrailingElseWrapper:
        return self if id is self._id else TrailingElseWrapper(self._id, self._prefix, self._markers, self._statement, self._else_block)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> TrailingElseWrapper:
        return self if prefix is self._prefix else TrailingElseWrapper(self._id, self._prefix, self._markers, self._statement, self._else_block)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> TrailingElseWrapper:
        return self if markers is self._markers else TrailingElseWrapper(self._id, self._prefix, self._markers, self._statement, self._else_block)

    _statement: Statement

    @property
    def statement(self) -> Statement:
        return self._statement

    def with_statement(self, statement: Statement) -> TrailingElseWrapper:
        return self if statement is self._statement else TrailingElseWrapper(self._id, self._prefix, self._markers, self._statement, self._else_block)

    _else_block: JLeftPadded[Block]

    @property
    def else_block(self) -> Block:
        return self._else_block.element

    def with_else_block(self, else_block: Block) -> TrailingElseWrapper:
        return self.padding.with_else_block(JLeftPadded.with_element(self._else_block, else_block))

    @dataclass
    class PaddingHelper:
        _t: TrailingElseWrapper

        @property
        def else_block(self) -> JLeftPadded[Block]:
            return self._t._else_block

        def with_else_block(self, else_block: JLeftPadded[Block]) -> TrailingElseWrapper:
            return self._t if self._t._else_block is else_block else TrailingElseWrapper(self._t.id, self._t.prefix, self._t.markers, self._t.statement, else_block)

    _padding: weakref.ReferenceType[TrailingElseWrapper.PaddingHelper] = None

    @property
    def padding(self) -> TrailingElseWrapper.PaddingHelper:
        p: TrailingElseWrapper.PaddingHelper
        if self._padding is None:
            p = TrailingElseWrapper.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = TrailingElseWrapper.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class ComprehensionExpression(Py, Expression):
    class Kind(Enum):
        LIST = 0
        SET = 1
        DICT = 2
        GENERATOR = 3

    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> ComprehensionExpression:
        return self if id is self._id else ComprehensionExpression(self._id, self._prefix, self._markers, self._kind, self._result, self._clauses, self._suffix, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> ComprehensionExpression:
        return self if prefix is self._prefix else ComprehensionExpression(self._id, self._prefix, self._markers, self._kind, self._result, self._clauses, self._suffix, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> ComprehensionExpression:
        return self if markers is self._markers else ComprehensionExpression(self._id, self._prefix, self._markers, self._kind, self._result, self._clauses, self._suffix, self._type)

    _kind: Kind

    @property
    def kind(self) -> Kind:
        return self._kind

    def with_kind(self, kind: Kind) -> ComprehensionExpression:
        return self if kind is self._kind else ComprehensionExpression(self._id, self._prefix, self._markers, self._kind, self._result, self._clauses, self._suffix, self._type)

    _result: Expression

    @property
    def result(self) -> Expression:
        return self._result

    def with_result(self, result: Expression) -> ComprehensionExpression:
        return self if result is self._result else ComprehensionExpression(self._id, self._prefix, self._markers, self._kind, self._result, self._clauses, self._suffix, self._type)

    _clauses: List[Clause]

    @property
    def clauses(self) -> List[Clause]:
        return self._clauses

    def with_clauses(self, clauses: List[Clause]) -> ComprehensionExpression:
        return self if clauses is self._clauses else ComprehensionExpression(self._id, self._prefix, self._markers, self._kind, self._result, self._clauses, self._suffix, self._type)

    _suffix: Space

    @property
    def suffix(self) -> Space:
        return self._suffix

    def with_suffix(self, suffix: Space) -> ComprehensionExpression:
        return self if suffix is self._suffix else ComprehensionExpression(self._id, self._prefix, self._markers, self._kind, self._result, self._clauses, self._suffix, self._type)

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> ComprehensionExpression:
        return self if type is self._type else ComprehensionExpression(self._id, self._prefix, self._markers, self._kind, self._result, self._clauses, self._suffix, self._type)

    @dataclass(frozen=True, eq=False)
    class Condition(Py):
        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> ComprehensionExpression.Condition:
            return self if id is self._id else ComprehensionExpression.Condition(self._id, self._prefix, self._markers, self._expression)

        _prefix: Space

        @property
        def prefix(self) -> Space:
            return self._prefix

        def with_prefix(self, prefix: Space) -> ComprehensionExpression.Condition:
            return self if prefix is self._prefix else ComprehensionExpression.Condition(self._id, self._prefix, self._markers, self._expression)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> ComprehensionExpression.Condition:
            return self if markers is self._markers else ComprehensionExpression.Condition(self._id, self._prefix, self._markers, self._expression)

        _expression: Expression

        @property
        def expression(self) -> Expression:
            return self._expression

        def with_expression(self, expression: Expression) -> ComprehensionExpression.Condition:
            return self if expression is self._expression else ComprehensionExpression.Condition(self._id, self._prefix, self._markers, self._expression)

    @dataclass(frozen=True, eq=False)
    class Clause(Py):
        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> ComprehensionExpression.Clause:
            return self if id is self._id else ComprehensionExpression.Clause(self._id, self._prefix, self._markers, self._iterator_variable, self._iterated_list, self._conditions)

        _prefix: Space

        @property
        def prefix(self) -> Space:
            return self._prefix

        def with_prefix(self, prefix: Space) -> ComprehensionExpression.Clause:
            return self if prefix is self._prefix else ComprehensionExpression.Clause(self._id, self._prefix, self._markers, self._iterator_variable, self._iterated_list, self._conditions)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> ComprehensionExpression.Clause:
            return self if markers is self._markers else ComprehensionExpression.Clause(self._id, self._prefix, self._markers, self._iterator_variable, self._iterated_list, self._conditions)

        _iterator_variable: Expression

        @property
        def iterator_variable(self) -> Expression:
            return self._iterator_variable

        def with_iterator_variable(self, iterator_variable: Expression) -> ComprehensionExpression.Clause:
            return self if iterator_variable is self._iterator_variable else ComprehensionExpression.Clause(self._id, self._prefix, self._markers, self._iterator_variable, self._iterated_list, self._conditions)

        _iterated_list: JLeftPadded[Expression]

        @property
        def iterated_list(self) -> Expression:
            return self._iterated_list.element

        def with_iterated_list(self, iterated_list: Expression) -> ComprehensionExpression.Clause:
            return self.padding.with_iterated_list(JLeftPadded.with_element(self._iterated_list, iterated_list))

        _conditions: Optional[List[ComprehensionExpression.Condition]]

        @property
        def conditions(self) -> Optional[List[ComprehensionExpression.Condition]]:
            return self._conditions

        def with_conditions(self, conditions: Optional[List[ComprehensionExpression.Condition]]) -> ComprehensionExpression.Clause:
            return self if conditions is self._conditions else ComprehensionExpression.Clause(self._id, self._prefix, self._markers, self._iterator_variable, self._iterated_list, self._conditions)

        @dataclass
        class PaddingHelper:
            _t: ComprehensionExpression.Clause

            @property
            def iterated_list(self) -> JLeftPadded[Expression]:
                return self._t._iterated_list

            def with_iterated_list(self, iterated_list: JLeftPadded[Expression]) -> ComprehensionExpression.Clause:
                return self._t if self._t._iterated_list is iterated_list else ComprehensionExpression.Clause(self._t.id, self._t.prefix, self._t.markers, self._t.iterator_variable, iterated_list, self._t.conditions)

    _padding: weakref.ReferenceType[Clause.PaddingHelper] = None

    @property
    def padding(self) -> Clause.PaddingHelper:
        p: ComprehensionExpression.Clause.PaddingHelper
        if self._padding is None:
            p = ComprehensionExpression.Clause.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = ComprehensionExpression.Clause.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class AwaitExpression(Py, Expression):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> AwaitExpression:
        return self if id is self._id else AwaitExpression(self._id, self._prefix, self._markers, self._expression, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> AwaitExpression:
        return self if prefix is self._prefix else AwaitExpression(self._id, self._prefix, self._markers, self._expression, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> AwaitExpression:
        return self if markers is self._markers else AwaitExpression(self._id, self._prefix, self._markers, self._expression, self._type)

    _expression: Expression

    @property
    def expression(self) -> Expression:
        return self._expression

    def with_expression(self, expression: Expression) -> AwaitExpression:
        return self if expression is self._expression else AwaitExpression(self._id, self._prefix, self._markers, self._expression, self._type)

    _type: JavaType

    @property
    def type(self) -> JavaType:
        return self._type

    def with_type(self, type: JavaType) -> AwaitExpression:
        return self if type is self._type else AwaitExpression(self._id, self._prefix, self._markers, self._expression, self._type)

@dataclass(frozen=True, eq=False)
class YieldExpression(Py, Expression):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> YieldExpression:
        return self if id is self._id else YieldExpression(self._id, self._prefix, self._markers, self._from, self._expressions, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> YieldExpression:
        return self if prefix is self._prefix else YieldExpression(self._id, self._prefix, self._markers, self._from, self._expressions, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> YieldExpression:
        return self if markers is self._markers else YieldExpression(self._id, self._prefix, self._markers, self._from, self._expressions, self._type)

    _from: JLeftPadded[bool]

    @property
    def from_(self) -> bool:
        return self._from.element

    def with_from(self, from_: bool) -> YieldExpression:
        return self.padding.with_from(JLeftPadded.with_element(self._from, from_))

    _expressions: List[JRightPadded[Expression]]

    @property
    def expressions(self) -> List[Expression]:
        return JRightPadded.get_elements(self._expressions)

    def with_expressions(self, expressions: List[Expression]) -> YieldExpression:
        return self.padding.with_expressions(JRightPadded.with_elements(self._expressions, expressions))

    _type: JavaType

    @property
    def type(self) -> JavaType:
        return self._type

    def with_type(self, type: JavaType) -> YieldExpression:
        return self if type is self._type else YieldExpression(self._id, self._prefix, self._markers, self._from, self._expressions, self._type)

    @dataclass
    class PaddingHelper:
        _t: YieldExpression

        @property
        def from_(self) -> JLeftPadded[bool]:
            return self._t._from

        def with_from(self, from_: JLeftPadded[bool]) -> YieldExpression:
            return self._t if self._t._from is from_ else YieldExpression(self._t.id, self._t.prefix, self._t.markers, from_, self._t._expressions, self._t.type)

        @property
        def expressions(self) -> List[JRightPadded[Expression]]:
            return self._t._expressions

        def with_expressions(self, expressions: List[JRightPadded[Expression]]) -> YieldExpression:
            return self._t if self._t._expressions is expressions else YieldExpression(self._t.id, self._t.prefix, self._t.markers, self._t._from, expressions, self._t.type)

    _padding: weakref.ReferenceType[YieldExpression.PaddingHelper] = None

    @property
    def padding(self) -> YieldExpression.PaddingHelper:
        p: YieldExpression.PaddingHelper
        if self._padding is None:
            p = YieldExpression.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = YieldExpression.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class VariableScopeStatement(Py, Statement):
    class Kind(Enum):
        GLOBAL = 0
        NONLOCAL = 1

    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> VariableScopeStatement:
        return self if id is self._id else VariableScopeStatement(self._id, self._prefix, self._markers, self._kind, self._names)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> VariableScopeStatement:
        return self if prefix is self._prefix else VariableScopeStatement(self._id, self._prefix, self._markers, self._kind, self._names)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> VariableScopeStatement:
        return self if markers is self._markers else VariableScopeStatement(self._id, self._prefix, self._markers, self._kind, self._names)

    _kind: Kind

    @property
    def kind(self) -> Kind:
        return self._kind

    def with_kind(self, kind: Kind) -> VariableScopeStatement:
        return self if kind is self._kind else VariableScopeStatement(self._id, self._prefix, self._markers, self._kind, self._names)

    _names: List[JRightPadded[Identifier]]

    @property
    def names(self) -> List[Identifier]:
        return JRightPadded.get_elements(self._names)

    def with_names(self, names: List[Identifier]) -> VariableScopeStatement:
        return self.padding.with_names(JRightPadded.with_elements(self._names, names))

    @dataclass
    class PaddingHelper:
        _t: VariableScopeStatement

        @property
        def names(self) -> List[JRightPadded[Identifier]]:
            return self._t._names

        def with_names(self, names: List[JRightPadded[Identifier]]) -> VariableScopeStatement:
            return self._t if self._t._names is names else VariableScopeStatement(self._t.id, self._t.prefix, self._t.markers, self._t.kind, names)

    _padding: weakref.ReferenceType[VariableScopeStatement.PaddingHelper] = None

    @property
    def padding(self) -> VariableScopeStatement.PaddingHelper:
        p: VariableScopeStatement.PaddingHelper
        if self._padding is None:
            p = VariableScopeStatement.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = VariableScopeStatement.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class AssertStatement(Py, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> AssertStatement:
        return self if id is self._id else AssertStatement(self._id, self._prefix, self._markers, self._expressions)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> AssertStatement:
        return self if prefix is self._prefix else AssertStatement(self._id, self._prefix, self._markers, self._expressions)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> AssertStatement:
        return self if markers is self._markers else AssertStatement(self._id, self._prefix, self._markers, self._expressions)

    _expressions: List[JRightPadded[Expression]]

    @property
    def expressions(self) -> List[Expression]:
        return JRightPadded.get_elements(self._expressions)

    def with_expressions(self, expressions: List[Expression]) -> AssertStatement:
        return self.padding.with_expressions(JRightPadded.with_elements(self._expressions, expressions))

    @dataclass
    class PaddingHelper:
        _t: AssertStatement

        @property
        def expressions(self) -> List[JRightPadded[Expression]]:
            return self._t._expressions

        def with_expressions(self, expressions: List[JRightPadded[Expression]]) -> AssertStatement:
            return self._t if self._t._expressions is expressions else AssertStatement(self._t.id, self._t.prefix, self._t.markers, expressions)

    _padding: weakref.ReferenceType[AssertStatement.PaddingHelper] = None

    @property
    def padding(self) -> AssertStatement.PaddingHelper:
        p: AssertStatement.PaddingHelper
        if self._padding is None:
            p = AssertStatement.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = AssertStatement.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class DelStatement(Py, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> DelStatement:
        return self if id is self._id else DelStatement(self._id, self._prefix, self._markers, self._targets)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> DelStatement:
        return self if prefix is self._prefix else DelStatement(self._id, self._prefix, self._markers, self._targets)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> DelStatement:
        return self if markers is self._markers else DelStatement(self._id, self._prefix, self._markers, self._targets)

    _targets: List[JRightPadded[Expression]]

    @property
    def targets(self) -> List[Expression]:
        return JRightPadded.get_elements(self._targets)

    def with_targets(self, targets: List[Expression]) -> DelStatement:
        return self.padding.with_targets(JRightPadded.with_elements(self._targets, targets))

    @dataclass
    class PaddingHelper:
        _t: DelStatement

        @property
        def targets(self) -> List[JRightPadded[Expression]]:
            return self._t._targets

        def with_targets(self, targets: List[JRightPadded[Expression]]) -> DelStatement:
            return self._t if self._t._targets is targets else DelStatement(self._t.id, self._t.prefix, self._t.markers, targets)

    _padding: weakref.ReferenceType[DelStatement.PaddingHelper] = None

    @property
    def padding(self) -> DelStatement.PaddingHelper:
        p: DelStatement.PaddingHelper
        if self._padding is None:
            p = DelStatement.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = DelStatement.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class SpecialParameter(Py, TypeTree):
    class Kind(Enum):
        KWARGS = 0
        ARGS = 1

    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> SpecialParameter:
        return self if id is self._id else SpecialParameter(self._id, self._prefix, self._markers, self._kind, self._type_hint, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> SpecialParameter:
        return self if prefix is self._prefix else SpecialParameter(self._id, self._prefix, self._markers, self._kind, self._type_hint, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> SpecialParameter:
        return self if markers is self._markers else SpecialParameter(self._id, self._prefix, self._markers, self._kind, self._type_hint, self._type)

    _kind: Kind

    @property
    def kind(self) -> Kind:
        return self._kind

    def with_kind(self, kind: Kind) -> SpecialParameter:
        return self if kind is self._kind else SpecialParameter(self._id, self._prefix, self._markers, self._kind, self._type_hint, self._type)

    _type_hint: Optional[TypeHint]

    @property
    def type_hint(self) -> Optional[TypeHint]:
        return self._type_hint

    def with_type_hint(self, type_hint: Optional[TypeHint]) -> SpecialParameter:
        return self if type_hint is self._type_hint else SpecialParameter(self._id, self._prefix, self._markers, self._kind, self._type_hint, self._type)

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> SpecialParameter:
        return self if type is self._type else SpecialParameter(self._id, self._prefix, self._markers, self._kind, self._type_hint, self._type)

@dataclass(frozen=True, eq=False)
class SpecialArgument(Py, Expression):
    class Kind(Enum):
        KWARGS = 0
        ARGS = 1

    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> SpecialArgument:
        return self if id is self._id else SpecialArgument(self._id, self._prefix, self._markers, self._kind, self._expression, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> SpecialArgument:
        return self if prefix is self._prefix else SpecialArgument(self._id, self._prefix, self._markers, self._kind, self._expression, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> SpecialArgument:
        return self if markers is self._markers else SpecialArgument(self._id, self._prefix, self._markers, self._kind, self._expression, self._type)

    _kind: Kind

    @property
    def kind(self) -> Kind:
        return self._kind

    def with_kind(self, kind: Kind) -> SpecialArgument:
        return self if kind is self._kind else SpecialArgument(self._id, self._prefix, self._markers, self._kind, self._expression, self._type)

    _expression: Expression

    @property
    def expression(self) -> Expression:
        return self._expression

    def with_expression(self, expression: Expression) -> SpecialArgument:
        return self if expression is self._expression else SpecialArgument(self._id, self._prefix, self._markers, self._kind, self._expression, self._type)

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> SpecialArgument:
        return self if type is self._type else SpecialArgument(self._id, self._prefix, self._markers, self._kind, self._expression, self._type)

@dataclass(frozen=True, eq=False)
class NamedArgument(Py, Expression):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> NamedArgument:
        return self if id is self._id else NamedArgument(self._id, self._prefix, self._markers, self._name, self._value, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> NamedArgument:
        return self if prefix is self._prefix else NamedArgument(self._id, self._prefix, self._markers, self._name, self._value, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> NamedArgument:
        return self if markers is self._markers else NamedArgument(self._id, self._prefix, self._markers, self._name, self._value, self._type)

    _name: Identifier

    @property
    def name(self) -> Identifier:
        return self._name

    def with_name(self, name: Identifier) -> NamedArgument:
        return self if name is self._name else NamedArgument(self._id, self._prefix, self._markers, self._name, self._value, self._type)

    _value: JLeftPadded[Expression]

    @property
    def value(self) -> Expression:
        return self._value.element

    def with_value(self, value: Expression) -> NamedArgument:
        return self.padding.with_value(JLeftPadded.with_element(self._value, value))

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> NamedArgument:
        return self if type is self._type else NamedArgument(self._id, self._prefix, self._markers, self._name, self._value, self._type)

    @dataclass
    class PaddingHelper:
        _t: NamedArgument

        @property
        def value(self) -> JLeftPadded[Expression]:
            return self._t._value

        def with_value(self, value: JLeftPadded[Expression]) -> NamedArgument:
            return self._t if self._t._value is value else NamedArgument(self._t.id, self._t.prefix, self._t.markers, self._t.name, value, self._t.type)

    _padding: weakref.ReferenceType[NamedArgument.PaddingHelper] = None

    @property
    def padding(self) -> NamedArgument.PaddingHelper:
        p: NamedArgument.PaddingHelper
        if self._padding is None:
            p = NamedArgument.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = NamedArgument.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class TypeHintedExpression(Py, Expression):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> TypeHintedExpression:
        return self if id is self._id else TypeHintedExpression(self._id, self._prefix, self._markers, self._type_hint, self._expression, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> TypeHintedExpression:
        return self if prefix is self._prefix else TypeHintedExpression(self._id, self._prefix, self._markers, self._type_hint, self._expression, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> TypeHintedExpression:
        return self if markers is self._markers else TypeHintedExpression(self._id, self._prefix, self._markers, self._type_hint, self._expression, self._type)

    _type_hint: TypeHint

    @property
    def type_hint(self) -> TypeHint:
        return self._type_hint

    def with_type_hint(self, type_hint: TypeHint) -> TypeHintedExpression:
        return self if type_hint is self._type_hint else TypeHintedExpression(self._id, self._prefix, self._markers, self._type_hint, self._expression, self._type)

    _expression: Expression

    @property
    def expression(self) -> Expression:
        return self._expression

    def with_expression(self, expression: Expression) -> TypeHintedExpression:
        return self if expression is self._expression else TypeHintedExpression(self._id, self._prefix, self._markers, self._type_hint, self._expression, self._type)

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> TypeHintedExpression:
        return self if type is self._type else TypeHintedExpression(self._id, self._prefix, self._markers, self._type_hint, self._expression, self._type)

@dataclass(frozen=True, eq=False)
class ErrorFromExpression(Py, Expression):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> ErrorFromExpression:
        return self if id is self._id else ErrorFromExpression(self._id, self._prefix, self._markers, self._error, self._from, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> ErrorFromExpression:
        return self if prefix is self._prefix else ErrorFromExpression(self._id, self._prefix, self._markers, self._error, self._from, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> ErrorFromExpression:
        return self if markers is self._markers else ErrorFromExpression(self._id, self._prefix, self._markers, self._error, self._from, self._type)

    _error: Expression

    @property
    def error(self) -> Expression:
        return self._error

    def with_error(self, error: Expression) -> ErrorFromExpression:
        return self if error is self._error else ErrorFromExpression(self._id, self._prefix, self._markers, self._error, self._from, self._type)

    _from: JLeftPadded[Expression]

    @property
    def from_(self) -> Expression:
        return self._from.element

    def with_from(self, from_: Expression) -> ErrorFromExpression:
        return self.padding.with_from(JLeftPadded.with_element(self._from, from_))

    _type: JavaType

    @property
    def type(self) -> JavaType:
        return self._type

    def with_type(self, type: JavaType) -> ErrorFromExpression:
        return self if type is self._type else ErrorFromExpression(self._id, self._prefix, self._markers, self._error, self._from, self._type)

    @dataclass
    class PaddingHelper:
        _t: ErrorFromExpression

        @property
        def from_(self) -> JLeftPadded[Expression]:
            return self._t._from

        def with_from(self, from_: JLeftPadded[Expression]) -> ErrorFromExpression:
            return self._t if self._t._from is from_ else ErrorFromExpression(self._t.id, self._t.prefix, self._t.markers, self._t.error, from_, self._t.type)

    _padding: weakref.ReferenceType[ErrorFromExpression.PaddingHelper] = None

    @property
    def padding(self) -> ErrorFromExpression.PaddingHelper:
        p: ErrorFromExpression.PaddingHelper
        if self._padding is None:
            p = ErrorFromExpression.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = ErrorFromExpression.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class MatchCase(Py, Expression):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> MatchCase:
        return self if id is self._id else MatchCase(self._id, self._prefix, self._markers, self._pattern, self._guard, self._type)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> MatchCase:
        return self if prefix is self._prefix else MatchCase(self._id, self._prefix, self._markers, self._pattern, self._guard, self._type)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> MatchCase:
        return self if markers is self._markers else MatchCase(self._id, self._prefix, self._markers, self._pattern, self._guard, self._type)

    _pattern: Pattern

    @property
    def pattern(self) -> Pattern:
        return self._pattern

    def with_pattern(self, pattern: Pattern) -> MatchCase:
        return self if pattern is self._pattern else MatchCase(self._id, self._prefix, self._markers, self._pattern, self._guard, self._type)

    _guard: Optional[JLeftPadded[Expression]]

    @property
    def guard(self) -> Optional[Expression]:
        return self._guard.element

    def with_guard(self, guard: Optional[Expression]) -> MatchCase:
        return self.padding.with_guard(JLeftPadded[Expression].with_element(self._guard, guard))

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> MatchCase:
        return self if type is self._type else MatchCase(self._id, self._prefix, self._markers, self._pattern, self._guard, self._type)

    @dataclass
    class PaddingHelper:
        _t: MatchCase

        @property
        def guard(self) -> Optional[JLeftPadded[Expression]]:
            return self._t._guard

        def with_guard(self, guard: Optional[JLeftPadded[Expression]]) -> MatchCase:
            return self._t if self._t._guard is guard else MatchCase(self._t.id, self._t.prefix, self._t.markers, self._t.pattern, guard, self._t.type)

    @dataclass(frozen=True, eq=False)
    class Pattern(Py, Expression):
        class Kind(Enum):
            AS = 0
            CAPTURE = 1
            CLASS = 2
            DOUBLE_STAR = 3
            GROUP = 4
            KEY_VALUE = 5
            KEYWORD = 6
            LITERAL = 7
            MAPPING = 8
            OR = 9
            SEQUENCE = 10
            SEQUENCE_LIST = 11
            SEQUENCE_TUPLE = 12
            STAR = 13
            VALUE = 14
            WILDCARD = 15

        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> MatchCase.Pattern:
            return self if id is self._id else MatchCase.Pattern(self._id, self._prefix, self._markers, self._kind, self._children, self._type)

        _prefix: Space

        @property
        def prefix(self) -> Space:
            return self._prefix

        def with_prefix(self, prefix: Space) -> MatchCase.Pattern:
            return self if prefix is self._prefix else MatchCase.Pattern(self._id, self._prefix, self._markers, self._kind, self._children, self._type)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> MatchCase.Pattern:
            return self if markers is self._markers else MatchCase.Pattern(self._id, self._prefix, self._markers, self._kind, self._children, self._type)

        _kind: Kind

        @property
        def kind(self) -> Kind:
            return self._kind

        def with_kind(self, kind: Kind) -> MatchCase.Pattern:
            return self if kind is self._kind else MatchCase.Pattern(self._id, self._prefix, self._markers, self._kind, self._children, self._type)

        _children: JContainer[Expression]

        @property
        def children(self) -> Expression:
            return self._children.element

        def with_children(self, children: Expression) -> MatchCase.Pattern:
            return self.padding.with_children(JContainer.with_element(self._children, children))

        _type: Optional[JavaType]

        @property
        def type(self) -> Optional[JavaType]:
            return self._type

        def with_type(self, type: Optional[JavaType]) -> MatchCase.Pattern:
            return self if type is self._type else MatchCase.Pattern(self._id, self._prefix, self._markers, self._kind, self._children, self._type)

        @dataclass
        class PaddingHelper:
            _t: MatchCase.Pattern

            @property
            def children(self) -> JContainer[Expression]:
                return self._t._children

            def with_children(self, children: JContainer[Expression]) -> MatchCase.Pattern:
                return self._t if self._t._children is children else MatchCase.Pattern(self._t.id, self._t.prefix, self._t.markers, self._t.kind, children, self._t.type)

    _padding: weakref.ReferenceType[Pattern.PaddingHelper] = None

    @property
    def padding(self) -> Pattern.PaddingHelper:
        p: MatchCase.Pattern.PaddingHelper
        if self._padding is None:
            p = MatchCase.Pattern.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = MatchCase.Pattern.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    _padding: weakref.ReferenceType[MatchCase.PaddingHelper] = None

    @property
    def padding(self) -> MatchCase.PaddingHelper:
        p: MatchCase.PaddingHelper
        if self._padding is None:
            p = MatchCase.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = MatchCase.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p
