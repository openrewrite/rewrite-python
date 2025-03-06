from dataclasses import dataclass, field
from typing import Any, Callable, List, cast, Union

from rewrite.java import Literal, P, J, Expression, Statement, JavaCoordinates, MethodDeclaration
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
            ReplaceTemplatingVisitor(lambda j: isinstance(j, Literal), '#{}', [2])))
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
            ReplaceTemplatingVisitor(lambda j: isinstance(j, Literal), '#{any()}', [parse_expression('2')])))
    )


def test_add_statement_after():
    rewrite_run(
        # language=python
        python(
            """\
            def f():
                pass
            """,
            """\
            def f():
                pass
                return
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(
            GenericTemplatingVisitor(
                lambda j: isinstance(j, MethodDeclaration) and len(j.body.statements) == 1,
                'return',
                coordinate_provider=lambda m: cast(MethodDeclaration, m).body.statements[0].get_coordinates().after())
        ))
    )


def test_add_statement_last():
    rewrite_run(
        # language=python
        python(
            """\
            def f():
                pass
                pass
            """,
            """\
            def f():
                pass
                pass
                return
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(
            GenericTemplatingVisitor(
                lambda j: isinstance(j, MethodDeclaration) and len(j.body.statements) == 2,
                'return',
                coordinate_provider=lambda m: cast(MethodDeclaration, m).body.get_coordinates().last_statement())
        ))
    )


def test_add_statement_first():
    rewrite_run(
        # language=python
        python(
            """\
            def f():
                pass
                pass
            """,
            """\
            def f():
                return
                pass
                pass
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(
            GenericTemplatingVisitor(
                lambda j: isinstance(j, MethodDeclaration) and len(j.body.statements) == 2,
                'return',
                coordinate_provider=lambda m: cast(MethodDeclaration, m).body.get_coordinates().first_statement())
        ))
    )


def test_add_statement_before():
    rewrite_run(
        # language=python
        python(
            """\
            def f():
                return
            """,
            """\
            def f():
                pass
                return
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(
            GenericTemplatingVisitor(
                lambda j: isinstance(j, MethodDeclaration) and len(j.body.statements) == 1,
                'pass',
                coordinate_provider=lambda m: cast(MethodDeclaration, m).body.statements[0].get_coordinates().before())
        ))
    )


def test_tree_substitution_named():
    rewrite_run(
        # language=python
        python(
            "a = 1",
            "a = 2 + 3 + 2",
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(
            ReplaceTemplatingVisitor(lambda j: isinstance(j, Literal), '#{name:any()} + #{any()} + #{name}', [parse_expression('2'), parse_expression('3')])))
    )


def parse_expression(code: str) -> J:
    return cast(ExpressionStatement, parse_statement(code)).expression


def parse_statement(code: str) -> J:
    return cast(CompilationUnit, next(iter(PythonParserBuilder().build().parse_strings(code)))).statements[0]


@dataclass
class ReplaceTemplatingVisitor(PythonVisitor[P]):
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

    def visit_statement(self, stmt: Statement, p: P) -> J:
        return self._template.apply(self.cursor, stmt.get_coordinates().replace(), self.params) if self.match(
            stmt) else stmt


@dataclass
class GenericTemplatingVisitor(PythonVisitor[P]):
    match: Callable[[J], bool]
    code: str
    coordinate_provider: Callable[[Union[Expression, Statement]], JavaCoordinates] = lambda j: j.get_coordinates().after()
    params: List[Any] = field(default_factory=list)

    debug: bool = False
    _template: PythonTemplate = field(init=False, repr=False)

    def __post_init__(self):
        self._template = PythonTemplate(
            self.code,
            on_after_variable_substitution=lambda code: print(code) if self.debug else None
        )

    def visit_expression(self, expr: Expression, p: P) -> J:
        return self._template.apply(self.cursor, self.coordinate_provider(expr), self.params) if self.match(
            expr) else expr

    def visit_statement(self, stmt: Statement, p: P) -> J:
        return self._template.apply(self.cursor, self.coordinate_provider(stmt), self.params) if self.match(
            stmt) else stmt
