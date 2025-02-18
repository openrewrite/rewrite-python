from dataclasses import dataclass, field
from typing import Any, Callable, List, cast

from rewrite.java import Literal, P, J, Expression
from rewrite.python import PythonVisitor, PythonTemplate, PythonParserBuilder, CompilationUnit, ExpressionStatement
from rewrite.test import from_visitor, RecipeSpec, rewrite_run, python


def test_string_substitution():
    rewrite_run(
        # language=python
        python(
            "a = 1",
            "a = 2",
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(
            ExpressionTemplatingVisitor(lambda j: isinstance(j, Literal), '#{}', [2])))
    )


def test_tree_substitution():
    rewrite_run(
        # language=python
        python(
            "a = 1",
            "a = 2",
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(
            ExpressionTemplatingVisitor(lambda j: isinstance(j, Literal), '#{any()}', [parse_expression('2')])))
    )


def test_tree_substitution_named():
    rewrite_run(
        # language=python
        python(
            "a = 1",
            "a = 2 + 2",
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(
            ExpressionTemplatingVisitor(lambda j: isinstance(j, Literal), '#{name:any()} + #{name}', [parse_expression('2')])))
    )


def parse_expression(code: str) -> J:
    return cast(ExpressionStatement,
                cast(CompilationUnit, next(iter(PythonParserBuilder().build().parse_strings(code)))).statements[
                    0]).expression


@dataclass
class ExpressionTemplatingVisitor(PythonVisitor[P]):
    match: Callable[[J], bool]
    code: str
    params: List[Any] = field(default_factory=list)
    debug: bool = False
    _template: PythonTemplate = field(init=False, repr=False)

    def __post_init__(self):
        self._template = PythonTemplate(
            self.code,
            on_after_variable_substitution=lambda code: print(code) if self.debug else None
        )

    def visit_expression(self, expr: Expression, p: P) -> J:
        return self._template.apply(self.cursor, expr.get_coordinates().replace(), self.params) if self.match(
            expr) else expr
