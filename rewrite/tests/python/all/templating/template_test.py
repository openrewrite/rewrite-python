from dataclasses import dataclass, field
from typing import Any, Callable, List

from rewrite.java import Literal, P, J, Expression
from rewrite.python import PythonVisitor, PythonTemplate
from rewrite.test import from_visitor, RecipeSpec, rewrite_run, python


def test_simple():
    # language=python
    rewrite_run(
        python(
            "a = 1",
            "a = 2",
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(ExpressionTemplatingVisitor(lambda j: isinstance(j, Literal), '#{}', [2])))
    )


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
        return self._template.apply(self.cursor, expr.get_coordinates().replace(), self.params) if self.match(expr) else expr
