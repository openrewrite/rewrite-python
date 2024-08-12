from __future__ import annotations

import weakref
from dataclasses import dataclass, replace
from pathlib import Path
from typing import List, Optional, Protocol, runtime_checkable, TYPE_CHECKING
from uuid import UUID
from enum import Enum

if TYPE_CHECKING:
    from ..visitor import PythonVisitor
from .support_types import *
from rewrite import Checksum, FileAttributes, SourceFile, Tree, TreeVisitor
from rewrite.marker import Markers
from rewrite.java.tree import *

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class ExceptionType(TypeTree):
    def __init__(self, id: UUID, prefix: Space, markers: Markers, type: JavaType, isExceptionGroup: bool, expression: Expression) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)
        object.__setattr__(self, '_type', type)
        object.__setattr__(self, '_isExceptionGroup', isExceptionGroup)
        object.__setattr__(self, '_expression', expression)

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

    _is_exception_group: bool

    @property
    def is_exception_group(self) -> bool:
        return self._is_exception_group

    def with_is_exception_group(self, is_exception_group: bool) -> ExceptionType:
        return self if is_exception_group is self._is_exception_group else replace(self, _is_exception_group=is_exception_group)

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
class TypeHint(TypeTree):
    def __init__(self, id: UUID, prefix: Space, markers: Markers, kind: 'TypeHint.Kind', expression: Expression, type: JavaType) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)
        object.__setattr__(self, '_kind', kind)
        object.__setattr__(self, '_expression', expression)
        object.__setattr__(self, '_type', type)

    class Kind(Enum):
        RETURN_TYPE = 0
        VARIABLE_TYPE = 1

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

    _kind: Kind

    @property
    def kind(self) -> Kind:
        return self._kind

    def with_kind(self, kind: Kind) -> TypeHint:
        return self if kind is self._kind else replace(self, _kind=kind)

    _expression: Expression

    @property
    def expression(self) -> Expression:
        return self._expression

    def with_expression(self, expression: Expression) -> TypeHint:
        return self if expression is self._expression else replace(self, _expression=expression)

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
class CompilationUnit(JavaSourceFile, SourceFile):
    def __init__(self, id: UUID, prefix: Space, markers: Markers, sourcePath: Path, fileAttributes: Optional[FileAttributes], charsetName: Optional[str], charsetBomMarked: bool, checksum: Optional[Checksum], imports: List[JRightPadded[Import]], statements: List[JRightPadded[Statement]], eof: Space) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)
        object.__setattr__(self, '_sourcePath', sourcePath)
        object.__setattr__(self, '_fileAttributes', fileAttributes)
        object.__setattr__(self, '_charsetName', charsetName)
        object.__setattr__(self, '_charsetBomMarked', charsetBomMarked)
        object.__setattr__(self, '_checksum', checksum)
        object.__setattr__(self, '_imports', imports)
        object.__setattr__(self, '_statements', statements)
        object.__setattr__(self, '_eof', eof)

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

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_compilation_unit(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class ExpressionStatement(Expression, Statement):
    def __init__(self, id: UUID, expression: Expression) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_expression', expression)

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
class KeyValue(Expression, TypedTree):
    def __init__(self, id: UUID, prefix: Space, markers: Markers, key: JRightPadded[Expression], value: Expression, type: Optional[JavaType]) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)
        object.__setattr__(self, '_key', key)
        object.__setattr__(self, '_value', value)
        object.__setattr__(self, '_type', type)

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
class DictLiteral(Expression, TypedTree):
    def __init__(self, id: UUID, prefix: Space, markers: Markers, elements: JContainer[KeyValue], type: Optional[JavaType]) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)
        object.__setattr__(self, '_elements', elements)
        object.__setattr__(self, '_type', type)

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

    _elements: JContainer[KeyValue]

    @property
    def elements(self) -> List[KeyValue]:
        return self._elements.elements

    def with_elements(self, elements: List[KeyValue]) -> DictLiteral:
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
        def elements(self) -> JContainer[KeyValue]:
            return self._t._elements

        def with_elements(self, elements: JContainer[KeyValue]) -> DictLiteral:
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
class PassStatement(Statement):
    def __init__(self, id: UUID, prefix: Space, markers: Markers) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)

    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> PassStatement:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> PassStatement:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> PassStatement:
        return self if markers is self._markers else replace(self, _markers=markers)

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_pass_statement(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class TrailingElseWrapper(Statement):
    def __init__(self, id: UUID, prefix: Space, markers: Markers, statement: Statement, elseBlock: JLeftPadded[Block]) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)
        object.__setattr__(self, '_statement', statement)
        object.__setattr__(self, '_elseBlock', elseBlock)

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
class ComprehensionExpression(Expression):
    def __init__(self, id: UUID, prefix: Space, markers: Markers, kind: 'ComprehensionExpression.Kind', result: Expression, clauses: 'List[ComprehensionExpression.Clause]', suffix: Space, type: Optional[JavaType]) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)
        object.__setattr__(self, '_kind', kind)
        object.__setattr__(self, '_result', result)
        object.__setattr__(self, '_clauses', clauses)
        object.__setattr__(self, '_suffix', suffix)
        object.__setattr__(self, '_type', type)

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
        def __init__(self, id: UUID, prefix: Space, markers: Markers, expression: Expression) -> None:
            # generated due to https://youtrack.jetbrains.com/issue/PY-62622
            object.__setattr__(self, '_id', id)
            object.__setattr__(self, '_prefix', prefix)
            object.__setattr__(self, '_markers', markers)
            object.__setattr__(self, '_expression', expression)

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
            return v.visit_comprehension_expression_condition(self, p)

    # noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
    @dataclass(frozen=True, eq=False)
    class Clause(Py):
        def __init__(self, id: UUID, prefix: Space, markers: Markers, iteratorVariable: Expression, iteratedList: JLeftPadded[Expression], conditions: Optional[List[ComprehensionExpression.Condition]]) -> None:
            # generated due to https://youtrack.jetbrains.com/issue/PY-62622
            object.__setattr__(self, '_id', id)
            object.__setattr__(self, '_prefix', prefix)
            object.__setattr__(self, '_markers', markers)
            object.__setattr__(self, '_iteratorVariable', iteratorVariable)
            object.__setattr__(self, '_iteratedList', iteratedList)
            object.__setattr__(self, '_conditions', conditions)

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
            return v.visit_comprehension_expression_clause(self, p)

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_comprehension_expression(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class AwaitExpression(Expression):
    def __init__(self, id: UUID, prefix: Space, markers: Markers, expression: Expression, type: JavaType) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)
        object.__setattr__(self, '_expression', expression)
        object.__setattr__(self, '_type', type)

    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> AwaitExpression:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> AwaitExpression:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> AwaitExpression:
        return self if markers is self._markers else replace(self, _markers=markers)

    _expression: Expression

    @property
    def expression(self) -> Expression:
        return self._expression

    def with_expression(self, expression: Expression) -> AwaitExpression:
        return self if expression is self._expression else replace(self, _expression=expression)

    _type: JavaType

    @property
    def type(self) -> JavaType:
        return self._type

    def with_type(self, type: JavaType) -> AwaitExpression:
        return self if type is self._type else replace(self, _type=type)

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_await_expression(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class YieldExpression(Expression):
    def __init__(self, id: UUID, prefix: Space, markers: Markers, from_: JLeftPadded[bool], expressions: List[JRightPadded[Expression]], type: JavaType) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)
        object.__setattr__(self, '_from', from_)
        object.__setattr__(self, '_expressions', expressions)
        object.__setattr__(self, '_type', type)

    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> YieldExpression:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> YieldExpression:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> YieldExpression:
        return self if markers is self._markers else replace(self, _markers=markers)

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
        return self if type is self._type else replace(self, _type=type)

    @dataclass
    class PaddingHelper:
        _t: YieldExpression

        @property
        def from_(self) -> JLeftPadded[bool]:
            return self._t._from

        def with_from(self, from_: JLeftPadded[bool]) -> YieldExpression:
            return self._t if self._t._from is from_ else replace(self._t, _from=from_)

        @property
        def expressions(self) -> List[JRightPadded[Expression]]:
            return self._t._expressions

        def with_expressions(self, expressions: List[JRightPadded[Expression]]) -> YieldExpression:
            return self._t if self._t._expressions is expressions else replace(self._t, _expressions=expressions)

    _padding: weakref.ReferenceType[PaddingHelper] = None

    @property
    def padding(self) -> PaddingHelper:
        p: YieldExpression.PaddingHelper
        if self._padding is None:
            p = YieldExpression.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            # noinspection PyProtectedMember
            if p is None or p._t != self:
                p = YieldExpression.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_yield_expression(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class VariableScopeStatement(Statement):
    def __init__(self, id: UUID, prefix: Space, markers: Markers, kind: 'VariableScopeStatement.Kind', names: List[JRightPadded[Identifier]]) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)
        object.__setattr__(self, '_kind', kind)
        object.__setattr__(self, '_names', names)

    class Kind(Enum):
        GLOBAL = 0
        NONLOCAL = 1

    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> VariableScopeStatement:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> VariableScopeStatement:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> VariableScopeStatement:
        return self if markers is self._markers else replace(self, _markers=markers)

    _kind: Kind

    @property
    def kind(self) -> Kind:
        return self._kind

    def with_kind(self, kind: Kind) -> VariableScopeStatement:
        return self if kind is self._kind else replace(self, _kind=kind)

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
            return self._t if self._t._names is names else replace(self._t, _names=names)

    _padding: weakref.ReferenceType[PaddingHelper] = None

    @property
    def padding(self) -> PaddingHelper:
        p: VariableScopeStatement.PaddingHelper
        if self._padding is None:
            p = VariableScopeStatement.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            # noinspection PyProtectedMember
            if p is None or p._t != self:
                p = VariableScopeStatement.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_variable_scope_statement(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class AssertStatement(Statement):
    def __init__(self, id: UUID, prefix: Space, markers: Markers, expressions: List[JRightPadded[Expression]]) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)
        object.__setattr__(self, '_expressions', expressions)

    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> AssertStatement:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> AssertStatement:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> AssertStatement:
        return self if markers is self._markers else replace(self, _markers=markers)

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
            return self._t if self._t._expressions is expressions else replace(self._t, _expressions=expressions)

    _padding: weakref.ReferenceType[PaddingHelper] = None

    @property
    def padding(self) -> PaddingHelper:
        p: AssertStatement.PaddingHelper
        if self._padding is None:
            p = AssertStatement.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            # noinspection PyProtectedMember
            if p is None or p._t != self:
                p = AssertStatement.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_assert_statement(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class DelStatement(Statement):
    def __init__(self, id: UUID, prefix: Space, markers: Markers, targets: List[JRightPadded[Expression]]) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)
        object.__setattr__(self, '_targets', targets)

    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> DelStatement:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> DelStatement:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> DelStatement:
        return self if markers is self._markers else replace(self, _markers=markers)

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
            return self._t if self._t._targets is targets else replace(self._t, _targets=targets)

    _padding: weakref.ReferenceType[PaddingHelper] = None

    @property
    def padding(self) -> PaddingHelper:
        p: DelStatement.PaddingHelper
        if self._padding is None:
            p = DelStatement.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            # noinspection PyProtectedMember
            if p is None or p._t != self:
                p = DelStatement.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_del_statement(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class SpecialParameter(TypeTree):
    def __init__(self, id: UUID, prefix: Space, markers: Markers, kind: 'SpecialParameter.Kind', typeHint: Optional[TypeHint], type: Optional[JavaType]) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)
        object.__setattr__(self, '_kind', kind)
        object.__setattr__(self, '_typeHint', typeHint)
        object.__setattr__(self, '_type', type)

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
class SpecialArgument(Expression):
    def __init__(self, id: UUID, prefix: Space, markers: Markers, kind: 'SpecialArgument.Kind', expression: Expression, type: Optional[JavaType]) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)
        object.__setattr__(self, '_kind', kind)
        object.__setattr__(self, '_expression', expression)
        object.__setattr__(self, '_type', type)

    class Kind(Enum):
        KWARGS = 0
        ARGS = 1

    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> SpecialArgument:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> SpecialArgument:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> SpecialArgument:
        return self if markers is self._markers else replace(self, _markers=markers)

    _kind: Kind

    @property
    def kind(self) -> Kind:
        return self._kind

    def with_kind(self, kind: Kind) -> SpecialArgument:
        return self if kind is self._kind else replace(self, _kind=kind)

    _expression: Expression

    @property
    def expression(self) -> Expression:
        return self._expression

    def with_expression(self, expression: Expression) -> SpecialArgument:
        return self if expression is self._expression else replace(self, _expression=expression)

    _type: Optional[JavaType]

    @property
    def type(self) -> Optional[JavaType]:
        return self._type

    def with_type(self, type: Optional[JavaType]) -> SpecialArgument:
        return self if type is self._type else replace(self, _type=type)

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_special_argument(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class NamedArgument(Expression):
    def __init__(self, id: UUID, prefix: Space, markers: Markers, name: Identifier, value: JLeftPadded[Expression], type: Optional[JavaType]) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)
        object.__setattr__(self, '_name', name)
        object.__setattr__(self, '_value', value)
        object.__setattr__(self, '_type', type)

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
class TypeHintedExpression(Expression):
    def __init__(self, id: UUID, prefix: Space, markers: Markers, typeHint: TypeHint, expression: Expression, type: Optional[JavaType]) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)
        object.__setattr__(self, '_typeHint', typeHint)
        object.__setattr__(self, '_expression', expression)
        object.__setattr__(self, '_type', type)

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
class ErrorFromExpression(Expression):
    def __init__(self, id: UUID, prefix: Space, markers: Markers, error: Expression, from_: JLeftPadded[Expression], type: JavaType) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)
        object.__setattr__(self, '_error', error)
        object.__setattr__(self, '_from', from_)
        object.__setattr__(self, '_type', type)

    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> ErrorFromExpression:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> ErrorFromExpression:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> ErrorFromExpression:
        return self if markers is self._markers else replace(self, _markers=markers)

    _error: Expression

    @property
    def error(self) -> Expression:
        return self._error

    def with_error(self, error: Expression) -> ErrorFromExpression:
        return self if error is self._error else replace(self, _error=error)

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
        return self if type is self._type else replace(self, _type=type)

    @dataclass
    class PaddingHelper:
        _t: ErrorFromExpression

        @property
        def from_(self) -> JLeftPadded[Expression]:
            return self._t._from

        def with_from(self, from_: JLeftPadded[Expression]) -> ErrorFromExpression:
            return self._t if self._t._from is from_ else replace(self._t, _from=from_)

    _padding: weakref.ReferenceType[PaddingHelper] = None

    @property
    def padding(self) -> PaddingHelper:
        p: ErrorFromExpression.PaddingHelper
        if self._padding is None:
            p = ErrorFromExpression.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            # noinspection PyProtectedMember
            if p is None or p._t != self:
                p = ErrorFromExpression.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    def accept_python(self, v: PythonVisitor[P], p: P) -> J:
        return v.visit_error_from_expression(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class MatchCase(Expression):
    def __init__(self, id: UUID, prefix: Space, markers: Markers, pattern: 'MatchCase.Pattern', guard: Optional[JLeftPadded[Expression]], type: Optional[JavaType]) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)
        object.__setattr__(self, '_pattern', pattern)
        object.__setattr__(self, '_guard', guard)
        object.__setattr__(self, '_type', type)

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
    class Pattern(Expression):
        def __init__(self, id: UUID, prefix: Space, markers: Markers, kind: 'MatchCase.Pattern.Kind', children: JContainer[Expression], type: Optional[JavaType]) -> None:
            # generated due to https://youtrack.jetbrains.com/issue/PY-62622
            object.__setattr__(self, '_id', id)
            object.__setattr__(self, '_prefix', prefix)
            object.__setattr__(self, '_markers', markers)
            object.__setattr__(self, '_kind', kind)
            object.__setattr__(self, '_children', children)
            object.__setattr__(self, '_type', type)

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
