from __future__ import annotations

import weakref
from dataclasses import dataclass, replace
from pathlib import Path
from typing import List, Optional, Protocol, runtime_checkable, TYPE_CHECKING
from uuid import UUID
from enum import Enum

if TYPE_CHECKING:
    from .visitor import PythonVisitor
from . import extensions
from .support_types import *
from rewrite import Checksum, FileAttributes, SourceFile, Tree, TreeVisitor, Markers, Cursor, PrintOutputCapture, PrinterFactory
from rewrite.java import *

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Binary(Py, Expression, TypedTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Binary:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Binary:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Binary:
        return self if markers is self._markers else replace(self, _markers=markers)

    _left: Expression

    @property
    def left(self) -> Expression:
        return self._left

    def with_left(self, left: Expression) -> Binary:
        return self if left is self._left else replace(self, _left=left)

    _operator: JLeftPadded[Type]

    @property
    def operator(self) -> Type:
        return self._operator.element

    def with_operator(self, operator: Type) -> Binary:
        return self.padding.with_operator(JLeftPadded.with_element(self._operator, operator))

    _negation: Optional[Space]

    @property
    def negation(self) -> Optional[Space]:
        return self._negation

    def with_negation(self, negation: Optional[Space]) -> Binary:
        return self if negation is self._negation else replace(self, _negation=negation)

    _right: Expression

    @property
    def right(self) -> Expression:
        return self._right

    def with_right(self, right: Expression) -> Binary:
        return self if right is self._right else replace(self, _right=right)

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> Binary:
        return self if type is self._type else replace(self, _type=type)

    class Type(Enum):
        In = 0
        Is = 1
        IsNot = 2
        NotIn = 3
        FloorDivision = 4
        MatrixMultiplication = 5
        Power = 6
        StringConcatenation = 7

    @dataclass
    class PaddingHelper:
        _t: Binary

        @property
        def operator(self) -> JLeftPadded[Binary.Type]:
            return self._t._operator

        def with_operator(self, operator: JLeftPadded[Binary.Type]) -> Binary:
            return self._t if self._t._operator is operator else replace(self._t, _operator=operator)

    _padding: weakref.ReferenceType[PaddingHelper] = None

    @property
    def padding(self) -> PaddingHelper:
        p: Binary.PaddingHelper
        if self._padding is None:
            p = Binary.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            # noinspection PyProtectedMember
            if p is None or p._t != self:
                p = Binary.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_python_binary(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class ExceptionType(Py, TypeTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> ExceptionType:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> ExceptionType:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> ExceptionType:
        return self if markers is self._markers else replace(self, _markers=markers)

    _type: JavaType

    @property
    def type(self) -> JavaType:
        return self._type

    def with_type(self, type: JavaType) -> ExceptionType:
        return self if type is self._type else replace(self, _type=type)

    _exception_group: bool

    @property
    def exception_group(self) -> bool:
        return self._exception_group

    def with_exception_group(self, exception_group: bool) -> ExceptionType:
        return self if exception_group is self._exception_group else replace(self, _exception_group=exception_group)

    _expression: Expression

    @property
    def expression(self) -> Expression:
        return self._expression

    def with_expression(self, expression: Expression) -> ExceptionType:
        return self if expression is self._expression else replace(self, _expression=expression)

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_exception_type(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class TypeHint(Py, TypeTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> TypeHint:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> TypeHint:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> TypeHint:
        return self if markers is self._markers else replace(self, _markers=markers)

    _type_tree: Expression

    @property
    def type_tree(self) -> Expression:
        return self._type_tree

    def with_type_tree(self, type_tree: Expression) -> TypeHint:
        return self if type_tree is self._type_tree else replace(self, _type_tree=type_tree)

    _type: JavaType

    @property
    def type(self) -> JavaType:
        return self._type

    def with_type(self, type: JavaType) -> TypeHint:
        return self if type is self._type else replace(self, _type=type)

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_type_hint(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class CompilationUnit(Py, JavaSourceFile, SourceFile):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> CompilationUnit:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> CompilationUnit:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> CompilationUnit:
        return self if markers is self._markers else replace(self, _markers=markers)

    _source_path: Path

    @property
    def source_path(self) -> Path:
        return self._source_path

    def with_source_path(self, source_path: Path) -> CompilationUnit:
        return self if source_path is self._source_path else replace(self, _source_path=source_path)

    _file_attributes: Optional[FileAttributes]

    @property
    def file_attributes(self) -> Optional[FileAttributes]:
        return self._file_attributes

    def with_file_attributes(self, file_attributes: Optional[FileAttributes]) -> CompilationUnit:
        return self if file_attributes is self._file_attributes else replace(self, _file_attributes=file_attributes)

    _charset_name: Optional[str]

    @property
    def charset_name(self) -> Optional[str]:
        return self._charset_name

    def with_charset_name(self, charset_name: Optional[str]) -> CompilationUnit:
        return self if charset_name is self._charset_name else replace(self, _charset_name=charset_name)

    _charset_bom_marked: bool

    @property
    def charset_bom_marked(self) -> bool:
        return self._charset_bom_marked

    def with_charset_bom_marked(self, charset_bom_marked: bool) -> CompilationUnit:
        return self if charset_bom_marked is self._charset_bom_marked else replace(self, _charset_bom_marked=charset_bom_marked)

    _checksum: Optional[Checksum]

    @property
    def checksum(self) -> Optional[Checksum]:
        return self._checksum

    def with_checksum(self, checksum: Optional[Checksum]) -> CompilationUnit:
        return self if checksum is self._checksum else replace(self, _checksum=checksum)

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
        return self if eof is self._eof else replace(self, _eof=eof)

    @dataclass
    class PaddingHelper:
        _t: CompilationUnit

        @property
        def imports(self) -> List[JRightPadded[Import]]:
            return self._t._imports

        def with_imports(self, imports: List[JRightPadded[Import]]) -> CompilationUnit:
            return self._t if self._t._imports is imports else replace(self._t, _imports=imports)

        @property
        def statements(self) -> List[JRightPadded[Statement]]:
            return self._t._statements

        def with_statements(self, statements: List[JRightPadded[Statement]]) -> CompilationUnit:
            return self._t if self._t._statements is statements else replace(self._t, _statements=statements)

    _padding: weakref.ReferenceType[PaddingHelper] = None

    @property
    def padding(self) -> PaddingHelper:
        p: CompilationUnit.PaddingHelper
        if self._padding is None:
            p = CompilationUnit.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            # noinspection PyProtectedMember
            if p is None or p._t != self:
                p = CompilationUnit.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    def printer(self, cursor: Cursor) -> TreeVisitor[Tree, PrintOutputCapture[P]]:
        return PrinterFactory.current().create_printer(cursor)

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_compilation_unit(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class ExpressionStatement(Py, Expression, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> ExpressionStatement:
        return self if id is self._id else replace(self, _id=id)

    _expression: Expression

    @property
    def expression(self) -> Expression:
        return self._expression

    def with_expression(self, expression: Expression) -> ExpressionStatement:
        return self if expression is self._expression else replace(self, _expression=expression)

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_expression_statement(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class StatementExpression(Py, Expression, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> StatementExpression:
        return self if id is self._id else replace(self, _id=id)

    _statement: Statement

    @property
    def statement(self) -> Statement:
        return self._statement

    def with_statement(self, statement: Statement) -> StatementExpression:
        return self if statement is self._statement else replace(self, _statement=statement)

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_statement_expression(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class MultiImport(Py, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> MultiImport:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> MultiImport:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> MultiImport:
        return self if markers is self._markers else replace(self, _markers=markers)

    _from: Optional[JRightPadded[NameTree]]

    @property
    def from_(self) -> Optional[NameTree]:
        return self._from.element

    def with_from(self, from_: Optional[NameTree]) -> MultiImport:
        return self.padding.with_from(JRightPadded.with_element(self._from, from_))

    _parenthesized: bool

    @property
    def parenthesized(self) -> bool:
        return self._parenthesized

    def with_parenthesized(self, parenthesized: bool) -> MultiImport:
        return self if parenthesized is self._parenthesized else replace(self, _parenthesized=parenthesized)

    _names: JContainer[Import]

    @property
    def names(self) -> List[Import]:
        return self._names.elements

    def with_names(self, names: List[Import]) -> MultiImport:
        return self.padding.with_names(JContainer.with_elements(self._names, names))

    @dataclass
    class PaddingHelper:
        _t: MultiImport

        @property
        def from_(self) -> Optional[JRightPadded[NameTree]]:
            return self._t._from

        def with_from(self, from_: Optional[JRightPadded[NameTree]]) -> MultiImport:
            return self._t if self._t._from is from_ else replace(self._t, _from=from_)

        @property
        def names(self) -> JContainer[Import]:
            return self._t._names

        def with_names(self, names: JContainer[Import]) -> MultiImport:
            return self._t if self._t._names is names else replace(self._t, _names=names)

    _padding: weakref.ReferenceType[PaddingHelper] = None

    @property
    def padding(self) -> PaddingHelper:
        p: MultiImport.PaddingHelper
        if self._padding is None:
            p = MultiImport.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            # noinspection PyProtectedMember
            if p is None or p._t != self:
                p = MultiImport.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_multi_import(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class KeyValue(Py, Expression, TypedTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> KeyValue:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> KeyValue:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> KeyValue:
        return self if markers is self._markers else replace(self, _markers=markers)

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
        return self if value is self._value else replace(self, _value=value)

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> KeyValue:
        return self if type is self._type else replace(self, _type=type)

    @dataclass
    class PaddingHelper:
        _t: KeyValue

        @property
        def key(self) -> JRightPadded[Expression]:
            return self._t._key

        def with_key(self, key: JRightPadded[Expression]) -> KeyValue:
            return self._t if self._t._key is key else replace(self._t, _key=key)

    _padding: weakref.ReferenceType[PaddingHelper] = None

    @property
    def padding(self) -> PaddingHelper:
        p: KeyValue.PaddingHelper
        if self._padding is None:
            p = KeyValue.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            # noinspection PyProtectedMember
            if p is None or p._t != self:
                p = KeyValue.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_key_value(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class DictLiteral(Py, Expression, TypedTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> DictLiteral:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> DictLiteral:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> DictLiteral:
        return self if markers is self._markers else replace(self, _markers=markers)

    _elements: JContainer[Expression]

    @property
    def elements(self) -> List[Expression]:
        return self._elements.elements

    def with_elements(self, elements: List[Expression]) -> DictLiteral:
        return self.padding.with_elements(JContainer.with_elements(self._elements, elements))

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> DictLiteral:
        return self if type is self._type else replace(self, _type=type)

    @dataclass
    class PaddingHelper:
        _t: DictLiteral

        @property
        def elements(self) -> JContainer[Expression]:
            return self._t._elements

        def with_elements(self, elements: JContainer[Expression]) -> DictLiteral:
            return self._t if self._t._elements is elements else replace(self._t, _elements=elements)

    _padding: weakref.ReferenceType[PaddingHelper] = None

    @property
    def padding(self) -> PaddingHelper:
        p: DictLiteral.PaddingHelper
        if self._padding is None:
            p = DictLiteral.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            # noinspection PyProtectedMember
            if p is None or p._t != self:
                p = DictLiteral.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_dict_literal(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class CollectionLiteral(Py, Expression, TypedTree):
    class Kind(Enum):
        LIST = 0
        SET = 1
        TUPLE = 2

    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> CollectionLiteral:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> CollectionLiteral:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> CollectionLiteral:
        return self if markers is self._markers else replace(self, _markers=markers)

    _kind: Kind

    @property
    def kind(self) -> Kind:
        return self._kind

    def with_kind(self, kind: Kind) -> CollectionLiteral:
        return self if kind is self._kind else replace(self, _kind=kind)

    _elements: JContainer[Expression]

    @property
    def elements(self) -> List[Expression]:
        return self._elements.elements

    def with_elements(self, elements: List[Expression]) -> CollectionLiteral:
        return self.padding.with_elements(JContainer.with_elements(self._elements, elements))

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> CollectionLiteral:
        return self if type is self._type else replace(self, _type=type)

    @dataclass
    class PaddingHelper:
        _t: CollectionLiteral

        @property
        def elements(self) -> JContainer[Expression]:
            return self._t._elements

        def with_elements(self, elements: JContainer[Expression]) -> CollectionLiteral:
            return self._t if self._t._elements is elements else replace(self._t, _elements=elements)

    _padding: weakref.ReferenceType[PaddingHelper] = None

    @property
    def padding(self) -> PaddingHelper:
        p: CollectionLiteral.PaddingHelper
        if self._padding is None:
            p = CollectionLiteral.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            # noinspection PyProtectedMember
            if p is None or p._t != self:
                p = CollectionLiteral.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_collection_literal(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class FormattedString(Py, Expression, TypedTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> FormattedString:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> FormattedString:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> FormattedString:
        return self if markers is self._markers else replace(self, _markers=markers)

    _delimiter: str

    @property
    def delimiter(self) -> str:
        return self._delimiter

    def with_delimiter(self, delimiter: str) -> FormattedString:
        return self if delimiter is self._delimiter else replace(self, _delimiter=delimiter)

    _parts: List[Expression]

    @property
    def parts(self) -> List[Expression]:
        return self._parts

    def with_parts(self, parts: List[Expression]) -> FormattedString:
        return self if parts is self._parts else replace(self, _parts=parts)

    # noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
    @dataclass(frozen=True, eq=False)
    class Value(Py, Expression, TypedTree):
        class Conversion(Enum):
            STR = 0
            REPR = 1
            ASCII = 2

        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> FormattedString.Value:
            return self if id is self._id else replace(self, _id=id)

        _prefix: Space

        @property
        def prefix(self) -> Space:
            return self._prefix

        def with_prefix(self, prefix: Space) -> FormattedString.Value:
            return self if prefix is self._prefix else replace(self, _prefix=prefix)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> FormattedString.Value:
            return self if markers is self._markers else replace(self, _markers=markers)

        _expression: JRightPadded[Expression]

        @property
        def expression(self) -> Expression:
            return self._expression.element

        def with_expression(self, expression: Expression) -> FormattedString.Value:
            return self.padding.with_expression(JRightPadded.with_element(self._expression, expression))

        _debug: Optional[JRightPadded[bool]]

        @property
        def debug(self) -> Optional[bool]:
            return self._debug.element

        def with_debug(self, debug: Optional[bool]) -> FormattedString.Value:
            return self.padding.with_debug(JRightPadded.with_element(self._debug, debug))

        _conversion: Optional[Conversion]

        @property
        def conversion(self) -> Optional[Conversion]:
            return self._conversion

        def with_conversion(self, conversion: Optional[Conversion]) -> FormattedString.Value:
            return self if conversion is self._conversion else replace(self, _conversion=conversion)

        _format: Optional[Expression]

        @property
        def format(self) -> Optional[Expression]:
            return self._format

        def with_format(self, format: Optional[Expression]) -> FormattedString.Value:
            return self if format is self._format else replace(self, _format=format)

        @dataclass
        class PaddingHelper:
            _t: FormattedString.Value

            @property
            def expression(self) -> JRightPadded[Expression]:
                return self._t._expression

            def with_expression(self, expression: JRightPadded[Expression]) -> FormattedString.Value:
                return self._t if self._t._expression is expression else replace(self._t, _expression=expression)

            @property
            def debug(self) -> Optional[JRightPadded[bool]]:
                return self._t._debug

            def with_debug(self, debug: Optional[JRightPadded[bool]]) -> FormattedString.Value:
                return self._t if self._t._debug is debug else replace(self._t, _debug=debug)

        _padding: weakref.ReferenceType[PaddingHelper] = None

        @property
        def padding(self) -> PaddingHelper:
            p: FormattedString.Value.PaddingHelper
            if self._padding is None:
                p = FormattedString.Value.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
            else:
                p = self._padding()
                # noinspection PyProtectedMember
                if p is None or p._t != self:
                    p = FormattedString.Value.PaddingHelper(self)
                    object.__setattr__(self, '_padding', weakref.ref(p))
            return p

        def accept_python(self, v: PythonVisitor[P], p: P) -> J:
            return v.visit_formatted_string_value(self, p)

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_formatted_string(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Pass(Py, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Pass:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Pass:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Pass:
        return self if markers is self._markers else replace(self, _markers=markers)

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_pass(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class TrailingElseWrapper(Py, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> TrailingElseWrapper:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> TrailingElseWrapper:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> TrailingElseWrapper:
        return self if markers is self._markers else replace(self, _markers=markers)

    _statement: Statement

    @property
    def statement(self) -> Statement:
        return self._statement

    def with_statement(self, statement: Statement) -> TrailingElseWrapper:
        return self if statement is self._statement else replace(self, _statement=statement)

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
            return self._t if self._t._else_block is else_block else replace(self._t, _else_block=else_block)

    _padding: weakref.ReferenceType[PaddingHelper] = None

    @property
    def padding(self) -> PaddingHelper:
        p: TrailingElseWrapper.PaddingHelper
        if self._padding is None:
            p = TrailingElseWrapper.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            # noinspection PyProtectedMember
            if p is None or p._t != self:
                p = TrailingElseWrapper.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_trailing_else_wrapper(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
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
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> ComprehensionExpression:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> ComprehensionExpression:
        return self if markers is self._markers else replace(self, _markers=markers)

    _kind: Kind

    @property
    def kind(self) -> Kind:
        return self._kind

    def with_kind(self, kind: Kind) -> ComprehensionExpression:
        return self if kind is self._kind else replace(self, _kind=kind)

    _result: Expression

    @property
    def result(self) -> Expression:
        return self._result

    def with_result(self, result: Expression) -> ComprehensionExpression:
        return self if result is self._result else replace(self, _result=result)

    _clauses: List[Clause]

    @property
    def clauses(self) -> List[Clause]:
        return self._clauses

    def with_clauses(self, clauses: List[Clause]) -> ComprehensionExpression:
        return self if clauses is self._clauses else replace(self, _clauses=clauses)

    _suffix: Space

    @property
    def suffix(self) -> Space:
        return self._suffix

    def with_suffix(self, suffix: Space) -> ComprehensionExpression:
        return self if suffix is self._suffix else replace(self, _suffix=suffix)

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> ComprehensionExpression:
        return self if type is self._type else replace(self, _type=type)

    # noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
    @dataclass(frozen=True, eq=False)
    class Condition(Py):
        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> ComprehensionExpression.Condition:
            return self if id is self._id else replace(self, _id=id)

        _prefix: Space

        @property
        def prefix(self) -> Space:
            return self._prefix

        def with_prefix(self, prefix: Space) -> ComprehensionExpression.Condition:
            return self if prefix is self._prefix else replace(self, _prefix=prefix)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> ComprehensionExpression.Condition:
            return self if markers is self._markers else replace(self, _markers=markers)

        _expression: Expression

        @property
        def expression(self) -> Expression:
            return self._expression

        def with_expression(self, expression: Expression) -> ComprehensionExpression.Condition:
            return self if expression is self._expression else replace(self, _expression=expression)

        def accept_python(self, v: PythonVisitor[P], p: P) -> J:
            return v.visit_comprehension_condition(self, p)

    # noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
    @dataclass(frozen=True, eq=False)
    class Clause(Py):
        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> ComprehensionExpression.Clause:
            return self if id is self._id else replace(self, _id=id)

        _prefix: Space

        @property
        def prefix(self) -> Space:
            return self._prefix

        def with_prefix(self, prefix: Space) -> ComprehensionExpression.Clause:
            return self if prefix is self._prefix else replace(self, _prefix=prefix)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> ComprehensionExpression.Clause:
            return self if markers is self._markers else replace(self, _markers=markers)

        _iterator_variable: Expression

        @property
        def iterator_variable(self) -> Expression:
            return self._iterator_variable

        def with_iterator_variable(self, iterator_variable: Expression) -> ComprehensionExpression.Clause:
            return self if iterator_variable is self._iterator_variable else replace(self, _iterator_variable=iterator_variable)

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
            return self if conditions is self._conditions else replace(self, _conditions=conditions)

        @dataclass
        class PaddingHelper:
            _t: ComprehensionExpression.Clause

            @property
            def iterated_list(self) -> JLeftPadded[Expression]:
                return self._t._iterated_list

            def with_iterated_list(self, iterated_list: JLeftPadded[Expression]) -> ComprehensionExpression.Clause:
                return self._t if self._t._iterated_list is iterated_list else replace(self._t, _iterated_list=iterated_list)

        _padding: weakref.ReferenceType[PaddingHelper] = None

        @property
        def padding(self) -> PaddingHelper:
            p: ComprehensionExpression.Clause.PaddingHelper
            if self._padding is None:
                p = ComprehensionExpression.Clause.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
            else:
                p = self._padding()
                # noinspection PyProtectedMember
                if p is None or p._t != self:
                    p = ComprehensionExpression.Clause.PaddingHelper(self)
                    object.__setattr__(self, '_padding', weakref.ref(p))
            return p

        def accept_python(self, v: PythonVisitor[P], p: P) -> J:
            return v.visit_comprehension_clause(self, p)

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_comprehension_expression(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Await(Py, Expression):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Await:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Await:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Await:
        return self if markers is self._markers else replace(self, _markers=markers)

    _expression: Expression

    @property
    def expression(self) -> Expression:
        return self._expression

    def with_expression(self, expression: Expression) -> Await:
        return self if expression is self._expression else replace(self, _expression=expression)

    _type: JavaType

    @property
    def type(self) -> JavaType:
        return self._type

    def with_type(self, type: JavaType) -> Await:
        return self if type is self._type else replace(self, _type=type)

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_await(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class YieldFrom(Py, Expression):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> YieldFrom:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> YieldFrom:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> YieldFrom:
        return self if markers is self._markers else replace(self, _markers=markers)

    _expression: Expression

    @property
    def expression(self) -> Expression:
        return self._expression

    def with_expression(self, expression: Expression) -> YieldFrom:
        return self if expression is self._expression else replace(self, _expression=expression)

    _type: JavaType

    @property
    def type(self) -> JavaType:
        return self._type

    def with_type(self, type: JavaType) -> YieldFrom:
        return self if type is self._type else replace(self, _type=type)

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_yield_from(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class VariableScope(Py, Statement):
    class Kind(Enum):
        GLOBAL = 0
        NONLOCAL = 1

    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> VariableScope:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> VariableScope:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> VariableScope:
        return self if markers is self._markers else replace(self, _markers=markers)

    _kind: Kind

    @property
    def kind(self) -> Kind:
        return self._kind

    def with_kind(self, kind: Kind) -> VariableScope:
        return self if kind is self._kind else replace(self, _kind=kind)

    _names: List[JRightPadded[Identifier]]

    @property
    def names(self) -> List[Identifier]:
        return JRightPadded.get_elements(self._names)

    def with_names(self, names: List[Identifier]) -> VariableScope:
        return self.padding.with_names(JRightPadded.with_elements(self._names, names))

    @dataclass
    class PaddingHelper:
        _t: VariableScope

        @property
        def names(self) -> List[JRightPadded[Identifier]]:
            return self._t._names

        def with_names(self, names: List[JRightPadded[Identifier]]) -> VariableScope:
            return self._t if self._t._names is names else replace(self._t, _names=names)

    _padding: weakref.ReferenceType[PaddingHelper] = None

    @property
    def padding(self) -> PaddingHelper:
        p: VariableScope.PaddingHelper
        if self._padding is None:
            p = VariableScope.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            # noinspection PyProtectedMember
            if p is None or p._t != self:
                p = VariableScope.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_variable_scope(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Del(Py, Statement):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Del:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Del:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Del:
        return self if markers is self._markers else replace(self, _markers=markers)

    _targets: List[JRightPadded[Expression]]

    @property
    def targets(self) -> List[Expression]:
        return JRightPadded.get_elements(self._targets)

    def with_targets(self, targets: List[Expression]) -> Del:
        return self.padding.with_targets(JRightPadded.with_elements(self._targets, targets))

    @dataclass
    class PaddingHelper:
        _t: Del

        @property
        def targets(self) -> List[JRightPadded[Expression]]:
            return self._t._targets

        def with_targets(self, targets: List[JRightPadded[Expression]]) -> Del:
            return self._t if self._t._targets is targets else replace(self._t, _targets=targets)

    _padding: weakref.ReferenceType[PaddingHelper] = None

    @property
    def padding(self) -> PaddingHelper:
        p: Del.PaddingHelper
        if self._padding is None:
            p = Del.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            # noinspection PyProtectedMember
            if p is None or p._t != self:
                p = Del.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_del(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
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
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> SpecialParameter:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> SpecialParameter:
        return self if markers is self._markers else replace(self, _markers=markers)

    _kind: Kind

    @property
    def kind(self) -> Kind:
        return self._kind

    def with_kind(self, kind: Kind) -> SpecialParameter:
        return self if kind is self._kind else replace(self, _kind=kind)

    _type_hint: Optional[TypeHint]

    @property
    def type_hint(self) -> Optional[TypeHint]:
        return self._type_hint

    def with_type_hint(self, type_hint: Optional[TypeHint]) -> SpecialParameter:
        return self if type_hint is self._type_hint else replace(self, _type_hint=type_hint)

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> SpecialParameter:
        return self if type is self._type else replace(self, _type=type)

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_special_parameter(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Star(Py, Expression):
    class Kind(Enum):
        LIST = 0
        DICT = 1

    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Star:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Star:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Star:
        return self if markers is self._markers else replace(self, _markers=markers)

    _kind: Kind

    @property
    def kind(self) -> Kind:
        return self._kind

    def with_kind(self, kind: Kind) -> Star:
        return self if kind is self._kind else replace(self, _kind=kind)

    _expression: Expression

    @property
    def expression(self) -> Expression:
        return self._expression

    def with_expression(self, expression: Expression) -> Star:
        return self if expression is self._expression else replace(self, _expression=expression)

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> Star:
        return self if type is self._type else replace(self, _type=type)

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_star(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class NamedArgument(Py, Expression):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> NamedArgument:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> NamedArgument:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> NamedArgument:
        return self if markers is self._markers else replace(self, _markers=markers)

    _name: Identifier

    @property
    def name(self) -> Identifier:
        return self._name

    def with_name(self, name: Identifier) -> NamedArgument:
        return self if name is self._name else replace(self, _name=name)

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
        return self if type is self._type else replace(self, _type=type)

    @dataclass
    class PaddingHelper:
        _t: NamedArgument

        @property
        def value(self) -> JLeftPadded[Expression]:
            return self._t._value

        def with_value(self, value: JLeftPadded[Expression]) -> NamedArgument:
            return self._t if self._t._value is value else replace(self._t, _value=value)

    _padding: weakref.ReferenceType[PaddingHelper] = None

    @property
    def padding(self) -> PaddingHelper:
        p: NamedArgument.PaddingHelper
        if self._padding is None:
            p = NamedArgument.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            # noinspection PyProtectedMember
            if p is None or p._t != self:
                p = NamedArgument.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_named_argument(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class TypeHintedExpression(Py, Expression):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> TypeHintedExpression:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> TypeHintedExpression:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> TypeHintedExpression:
        return self if markers is self._markers else replace(self, _markers=markers)

    _type_hint: TypeHint

    @property
    def type_hint(self) -> TypeHint:
        return self._type_hint

    def with_type_hint(self, type_hint: TypeHint) -> TypeHintedExpression:
        return self if type_hint is self._type_hint else replace(self, _type_hint=type_hint)

    _expression: Expression

    @property
    def expression(self) -> Expression:
        return self._expression

    def with_expression(self, expression: Expression) -> TypeHintedExpression:
        return self if expression is self._expression else replace(self, _expression=expression)

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> TypeHintedExpression:
        return self if type is self._type else replace(self, _type=type)

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_type_hinted_expression(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class ErrorFrom(Py, Expression):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> ErrorFrom:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> ErrorFrom:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> ErrorFrom:
        return self if markers is self._markers else replace(self, _markers=markers)

    _error: Expression

    @property
    def error(self) -> Expression:
        return self._error

    def with_error(self, error: Expression) -> ErrorFrom:
        return self if error is self._error else replace(self, _error=error)

    _from: JLeftPadded[Expression]

    @property
    def from_(self) -> Expression:
        return self._from.element

    def with_from(self, from_: Expression) -> ErrorFrom:
        return self.padding.with_from(JLeftPadded.with_element(self._from, from_))

    _type: JavaType

    @property
    def type(self) -> JavaType:
        return self._type

    def with_type(self, type: JavaType) -> ErrorFrom:
        return self if type is self._type else replace(self, _type=type)

    @dataclass
    class PaddingHelper:
        _t: ErrorFrom

        @property
        def from_(self) -> JLeftPadded[Expression]:
            return self._t._from

        def with_from(self, from_: JLeftPadded[Expression]) -> ErrorFrom:
            return self._t if self._t._from is from_ else replace(self._t, _from=from_)

    _padding: weakref.ReferenceType[PaddingHelper] = None

    @property
    def padding(self) -> PaddingHelper:
        p: ErrorFrom.PaddingHelper
        if self._padding is None:
            p = ErrorFrom.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            # noinspection PyProtectedMember
            if p is None or p._t != self:
                p = ErrorFrom.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_error_from(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class MatchCase(Py, Expression):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> MatchCase:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> MatchCase:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> MatchCase:
        return self if markers is self._markers else replace(self, _markers=markers)

    _pattern: Pattern

    @property
    def pattern(self) -> Pattern:
        return self._pattern

    def with_pattern(self, pattern: Pattern) -> MatchCase:
        return self if pattern is self._pattern else replace(self, _pattern=pattern)

    _guard: Optional[JLeftPadded[Expression]]

    @property
    def guard(self) -> Optional[Expression]:
        return self._guard.element

    def with_guard(self, guard: Optional[Expression]) -> MatchCase:
        return self.padding.with_guard(JLeftPadded.with_element(self._guard, guard))

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> MatchCase:
        return self if type is self._type else replace(self, _type=type)

    @dataclass
    class PaddingHelper:
        _t: MatchCase

        @property
        def guard(self) -> Optional[JLeftPadded[Expression]]:
            return self._t._guard

        def with_guard(self, guard: Optional[JLeftPadded[Expression]]) -> MatchCase:
            return self._t if self._t._guard is guard else replace(self._t, _guard=guard)

    _padding: weakref.ReferenceType[PaddingHelper] = None

    @property
    def padding(self) -> PaddingHelper:
        p: MatchCase.PaddingHelper
        if self._padding is None:
            p = MatchCase.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            # noinspection PyProtectedMember
            if p is None or p._t != self:
                p = MatchCase.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    # noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
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
            return self if id is self._id else replace(self, _id=id)

        _prefix: Space

        @property
        def prefix(self) -> Space:
            return self._prefix

        def with_prefix(self, prefix: Space) -> MatchCase.Pattern:
            return self if prefix is self._prefix else replace(self, _prefix=prefix)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> MatchCase.Pattern:
            return self if markers is self._markers else replace(self, _markers=markers)

        _kind: Kind

        @property
        def kind(self) -> Kind:
            return self._kind

        def with_kind(self, kind: Kind) -> MatchCase.Pattern:
            return self if kind is self._kind else replace(self, _kind=kind)

        _children: JContainer[Expression]

        @property
        def children(self) -> List[Expression]:
            return self._children.elements

        def with_children(self, children: List[Expression]) -> MatchCase.Pattern:
            return self.padding.with_children(JContainer.with_elements(self._children, children))

        _type: Optional[JavaType]

        @property
        def type(self) -> Optional[JavaType]:
            return self._type

        def with_type(self, type: Optional[JavaType]) -> MatchCase.Pattern:
            return self if type is self._type else replace(self, _type=type)

        @dataclass
        class PaddingHelper:
            _t: MatchCase.Pattern

            @property
            def children(self) -> JContainer[Expression]:
                return self._t._children

            def with_children(self, children: JContainer[Expression]) -> MatchCase.Pattern:
                return self._t if self._t._children is children else replace(self._t, _children=children)

        _padding: weakref.ReferenceType[PaddingHelper] = None

        @property
        def padding(self) -> PaddingHelper:
            p: MatchCase.Pattern.PaddingHelper
            if self._padding is None:
                p = MatchCase.Pattern.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
            else:
                p = self._padding()
                # noinspection PyProtectedMember
                if p is None or p._t != self:
                    p = MatchCase.Pattern.PaddingHelper(self)
                    object.__setattr__(self, '_padding', weakref.ref(p))
            return p

        def accept_python(self, v: PythonVisitor[P], p: P) -> J:
            return v.visit_match_case_pattern(self, p)

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_match_case(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Slice(Py, Expression, TypedTree):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Slice:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Slice:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Slice:
        return self if markers is self._markers else replace(self, _markers=markers)

    _start: Optional[JRightPadded[Expression]]

    @property
    def start(self) -> Optional[Expression]:
        return self._start.element

    def with_start(self, start: Optional[Expression]) -> Slice:
        return self.padding.with_start(JRightPadded.with_element(self._start, start))

    _stop: Optional[JRightPadded[Expression]]

    @property
    def stop(self) -> Optional[Expression]:
        return self._stop.element

    def with_stop(self, stop: Optional[Expression]) -> Slice:
        return self.padding.with_stop(JRightPadded.with_element(self._stop, stop))

    _step: Optional[JRightPadded[Expression]]

    @property
    def step(self) -> Optional[Expression]:
        return self._step.element

    def with_step(self, step: Optional[Expression]) -> Slice:
        return self.padding.with_step(JRightPadded.with_element(self._step, step))

    @dataclass
    class PaddingHelper:
        _t: Slice

        @property
        def start(self) -> Optional[JRightPadded[Expression]]:
            return self._t._start

        def with_start(self, start: Optional[JRightPadded[Expression]]) -> Slice:
            return self._t if self._t._start is start else replace(self._t, _start=start)

        @property
        def stop(self) -> Optional[JRightPadded[Expression]]:
            return self._t._stop

        def with_stop(self, stop: Optional[JRightPadded[Expression]]) -> Slice:
            return self._t if self._t._stop is stop else replace(self._t, _stop=stop)

        @property
        def step(self) -> Optional[JRightPadded[Expression]]:
            return self._t._step

        def with_step(self, step: Optional[JRightPadded[Expression]]) -> Slice:
            return self._t if self._t._step is step else replace(self._t, _step=step)

    _padding: weakref.ReferenceType[PaddingHelper] = None

    @property
    def padding(self) -> PaddingHelper:
        p: Slice.PaddingHelper
        if self._padding is None:
            p = Slice.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            # noinspection PyProtectedMember
            if p is None or p._t != self:
                p = Slice.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_slice(self, p)
