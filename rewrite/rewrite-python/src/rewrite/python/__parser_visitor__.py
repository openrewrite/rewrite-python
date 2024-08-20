import ast
from _ast import AST
from pathlib import Path
from typing import Optional, TypeVar, cast

import rewrite.java.tree as j
import rewrite.python.tree as py
from rewrite import random_id
from rewrite.java.tree import Space, JRightPadded, JContainer, JLeftPadded, JavaType, TextComment, J
from rewrite.marker import Markers

J2 = TypeVar('J2', bound=J)


class ParserVisitor(ast.NodeVisitor):
    _source: str
    _cursor: int = 0

    def __init__(self, source: str):
        super().__init__()
        self._source = source

    def visit_Assert(self, node):
        return j.Assert(
            random_id(),
            self.__source_before(),
            Markers.EMPTY,
            self.__convert(node.test),
            self.__pad_left(Space.EMPTY, self.__convert(node.msg)) if node.msg else None,
        )

    def visit_Constant(self, node):
        # noinspection PyTypeChecker
        type_: JavaType.Primitive = self.__map_type(node)
        return j.Literal(
            random_id(),
            Space.EMPTY,
            Markers.EMPTY,
            node.value,
            str(node.value),
            None,
            type_,
        )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> j.MethodDeclaration:
        body = j.Block(
            random_id(),
            Space.EMPTY,
            Markers.EMPTY,
            self.__pad_right(False, Space.EMPTY),
            [self.__pad_right(self.__convert(cast(AST, stmt)), Space.EMPTY) for stmt in node.body] if node.body else [
                self.__pad_right(j.Empty(random_id(), Space.EMPTY, Markers.EMPTY), Space.EMPTY)],
            Space.EMPTY
        )
        return_type_expression = self.visit(node.returns) if node.returns else None

        return j.MethodDeclaration(
            random_id(),
            Space([], ' '),
            Markers.EMPTY,
            [],
            [],
            None,
            return_type_expression,
            j.MethodDeclaration.IdentifierWithAnnotations(j.Identifier(
                random_id(),
                Space.EMPTY,
                Markers.EMPTY,
                [],
                node.name,
                None,
                None
            ), []),
            JContainer.empty(),
            None,
            body,
            None,
            self.__map_type(node),
        )

    def visit_Module(self, node: ast.Module) -> py.CompilationUnit:
        return py.CompilationUnit(
            random_id(),
            Space.EMPTY,
            Markers.EMPTY,
            Path("TODO"),
            None,
            None,
            False,
            None,
            [],
            [self.__pad_right(self.visit(cast(AST, stmt)), Space.EMPTY) for stmt in node.body] if node.body else [
                self.__pad_right(j.Empty(random_id(), Space.EMPTY, Markers.EMPTY), Space.EMPTY)],
            Space.EMPTY
        )

    def visit_Name(self, node):
        return j.Identifier(
            random_id(),
            Space.EMPTY,
            Markers.EMPTY,
            [],
            node.id,
            self.__map_type(node),
            None
        )

    def __convert(self, node) -> Optional[J]:
        if node:
            return self.visit(node)
        else:
            return None

    def __pad_right(self, tree, space: Space) -> JRightPadded[J2]:
        return JRightPadded(tree, space, Markers.EMPTY)

    def __pad_left(self, space: Space, tree) -> JLeftPadded[J2]:
        return JLeftPadded(space, tree, Markers.EMPTY)

    def __source_before(self) -> Space:
        prefix = None
        whitespace = []
        comments = []
        while self._cursor < len(self._source):
            char = self._source[self._cursor]
            if char.isspace():
                whitespace.append(char)
            elif char == '#':
                if comments:
                    comments[-1] = comments[-1].with_suffix('\n' + ''.join(whitespace))
                else:
                    prefix = ''.join(whitespace)
                whitespace = []
                comment = []
                while self._cursor < len(self._source) and self._source[self._cursor] != '\n':
                    comment.append(self._source[self._cursor])
                    self._cursor += 1
                comments.append(TextComment(False, ''.join(comment), '\n' if self._cursor < len(self._source) else '', Markers.EMPTY))
            else:
                break
            self._cursor += 1

        if not comments:
            prefix = ''.join(whitespace)
        elif whitespace:
            comments[-1] = comments[-1].with_suffix('\n' + ''.join(whitespace))
        return Space(comments, prefix)

    def __map_type(self, node) -> Optional[JavaType]:
        return None
