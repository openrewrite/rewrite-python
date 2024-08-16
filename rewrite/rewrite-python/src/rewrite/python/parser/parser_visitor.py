import ast
from pathlib import Path

import rewrite.java.tree as J
import rewrite.python.tree as Py
from rewrite import random_id
from rewrite.java.tree import Space, JRightPadded, JContainer
from rewrite.marker import Markers


def map_type(node):
    return None


class ParserVisitor(ast.NodeVisitor):
    _source: str
    _cursor: int = 0

    def __init__(self, source: str):
        super().__init__()
        self._source = source

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
            map_type(node),
        )

    def visit_Assign(self, node: ast.Assign):
        targets = [target.id for target in node.targets if isinstance(target, ast.Name)]
        value = node.value
        result = f"Assignment to: {', '.join(targets)} = {ast.dump(value)}"
        # Call generic_visit to continue the traversal
        self.generic_visit(node)
        return result

    def visit_Assert(self, node):
        return Py.AssertStatement(
            random_id(),
            Space.EMPTY,
            Markers.EMPTY,
            [JRightPadded(self.visit(expr), Space.EMPTY, Markers.EMPTY) for expr in ([node.test, node.msg] if node.msg else [node.test])]
        )

    def visit_Constant(self, node):
        return J.Literal(
            random_id(),
            Space.EMPTY,
            Markers.EMPTY,
            node.value,
            str(node.value),
            None,
            None
        )

    def visit_Name(self, node):
        return J.Identifier(
            random_id(),
            Space.EMPTY,
            Markers.EMPTY,
            [],
            node.id,
            None,
            None
        )