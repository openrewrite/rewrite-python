import ast
from pathlib import Path
from typing import Optional, TypeVar

import rewrite.java.tree as J
import rewrite.python.tree as Py
from rewrite import random_id
from rewrite.java.tree import Space, JRightPadded, JContainer, JLeftPadded
from rewrite.marker import Markers

J2 = TypeVar('J2', bound=J)


class ParserVisitor(ast.NodeVisitor):
    _source: str
    _cursor: int = 0

    def __init__(self, source: str):
        super().__init__()
        self._source = source

    def visit_Assert(self, node):
        return J.Assert(
            random_id(),
            Space.EMPTY,
            Markers.EMPTY,
            self.__convert(node.test),
            self.__convert(node.msg)
        )

    def visit_Assign(self, node: ast.Assign):
        targets = [target.id for target in node.targets if isinstance(target, ast.Name)]
        value = node.value
        result = f"Assignment to: {', '.join(targets)} = {ast.dump(value)}"
        # Call generic_visit to continue the traversal
        self.generic_visit(node)
        return result

    def visit_Constant(self, node):
        return J.Literal(
            random_id(),
            Space.EMPTY,
            Markers.EMPTY,
            node.value,
            str(node.value),
            None,
            None,  # FIXME
        )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> J.MethodDeclaration:
        body = J.Block(
            random_id(),
            Space.EMPTY,
            Markers.EMPTY,
            JRightPadded(False, Space.EMPTY, Markers.EMPTY),
            [JRightPadded(self.visit(stmt), Space.EMPTY, Markers.EMPTY) for stmt in node.body] if node.body else [
                JRightPadded(J.Empty(random_id(), Space.EMPTY, Markers.EMPTY), Space.EMPTY, Markers.EMPTY)],
            Space.EMPTY
        )
        return_type_expression = self.visit(node.returns) if node.returns else None

        return J.MethodDeclaration(
            random_id(),
            Space([], ' '),
            Markers.EMPTY,
            [],
            [],
            None,
            return_type_expression,
            J.MethodDeclaration.IdentifierWithAnnotations(J.Identifier(
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

    def visit_Module(self, node: ast.Module) -> Py.CompilationUnit:
        return Py.CompilationUnit(
            random_id(),
            Space.EMPTY,
            Markers.EMPTY,
            Path("TODO"),
            None,
            None,
            False,
            None,
            [],
            [JRightPadded(self.visit(stmt), Space.EMPTY, Markers.EMPTY) for stmt in node.body] if node.body else [
                JRightPadded(J.Empty(random_id(), Space.EMPTY, Markers.EMPTY), Space.EMPTY, Markers.EMPTY)]
            ,
            Space.EMPTY
        )

    def visit_Name(self, node):
        return J.Identifier(
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

    def __pad_right(self, node, space: Space) -> JRightPadded[J2]:
        return JRightPadded(self.__convert(node), space, Markers.EMPTY)

    def __pad_left(self, node, space: Space) -> JLeftPadded[J2]:
        return JLeftPadded(space, self.__convert(node), Markers.EMPTY)

    def __source_before(self) -> Space:
        result = []
        while self._cursor < len(self._source):
            char = self._source[self._cursor]
            if char.isspace():
                result.append(char)
            elif char == '#':
                # TODO create TextComment
                while self._cursor < len(self._source) and self._source[self._cursor] != '\n':
                    result.append(self._source[self._cursor])
                    self._cursor += 1
                result.append('\n')
            else:
                break
            self._cursor += 1
        return Space([], ''.join(result))

    def __map_type(self, node):
        return None
