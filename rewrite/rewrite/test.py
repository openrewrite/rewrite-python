from __future__ import annotations

import socket
import textwrap
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Optional, Callable, Iterable
from uuid import UUID

from rewrite import InMemoryExecutionContext, ParserInput, ParserBuilder, random_id, ParseError, ParseExceptionResult, \
    ExecutionContext, Recipe, TreeVisitor
from rewrite.python.parser import PythonParserBuilder


@dataclass(frozen=True, eq=False)
class SourceSpec:
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    _parser: ParserBuilder

    @property
    def parser(self) -> ParserBuilder:
        return self._parser

    _before: str

    @property
    def before(self) -> str:
        return self._before

    _after: Optional[Callable[[str], str]]

    @property
    def after(self) -> Optional[Callable[[str], str]]:
        return self._after

    _source_path: Optional[Path]

    @property
    def source_path(self) -> Optional[Path]:
        return self._source_path


@dataclass(frozen=True, eq=False)
class RecipeSpec:
    _recipe: Recipe = None

    @property
    def recipe(self) -> Recipe:
        return self._recipe

    def with_recipe(self, recipe: Recipe) -> RecipeSpec:
        return self if recipe is self._recipe else RecipeSpec(recipe)

    _parsers: Iterable[ParserBuilder] = field(default_factory=list)

    @property
    def parsers(self) -> Iterable[ParserBuilder]:
        return self._parsers

    def with_parsers(self, parsers: Iterable[ParserBuilder]) -> RecipeSpec:
        return self if parsers is self._parsers else RecipeSpec(self._recipe, parsers)


def rewrite_run(*source_specs: Iterable[SourceSpec], spec: RecipeSpec = None):
    from rewrite.remote import RemotingContext, RemotePrinterFactory
    from rewrite.remote.server import register_remoting_factories
    remoting_context = RemotingContext()
    register_remoting_factories()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 65432))
    remoting_context.connect(s)
    RemotePrinterFactory(remoting_context.client).set_current()

    try:
        ctx = InMemoryExecutionContext()
        ctx.put_message(ExecutionContext.REQUIRE_PRINT_EQUALS_INPUT, False)

        configured_parsers = {p.source_file_type: p for p in spec.parsers} if spec else {}
        parsers = {s.parser.source_file_type: configured_parsers.get(s.parser.source_file_type, s.parser) for source_spec in source_specs for s in source_spec}
        for source in source_specs:
            for source_spec in source:
                parser = parsers[source_spec.parser.source_file_type].build()
                source_path = source_spec.source_path if source_spec.source_path \
                    else parser.source_path_from_source_text(Path('.'), source_spec.before)
                for source_file in parser.parse_inputs(
                        [ParserInput(source_path, None, True, lambda: StringIO(source_spec.before))], None, ctx):
                    if isinstance(source_file, ParseError):
                        assert False, f'Parser threw an exception:\n%{source_file.markers.find_first(ParseExceptionResult).message}'
                    remoting_context.client.reset()
                    assert source_file.print_all() == source_spec.before

                    if spec:
                        source_file = spec.recipe.get_visitor().visit(source_file, ctx)

                    if source_spec.after is not None:
                        after = source_spec.after(source_file.print_all())
                        assert source_file.print_all() == after
                    else:
                        assert source_file.print_all() == source_spec.before
                    break
    except Exception:
        raise
    finally:
        remoting_context.close()


def python(before: str, after: str = None) -> list[SourceSpec]:
    return [SourceSpec(
        random_id(),
        PythonParserBuilder(),
        textwrap.dedent(before),
        None if after is None else lambda _: textwrap.dedent(after),
        None
    )]


def from_visitor(visitor: TreeVisitor[any, any]) -> Recipe:
    return AdHocRecipe(visitor)


@dataclass(frozen=True)
class AdHocRecipe(Recipe):
    visitor: TreeVisitor[any, any]

    def get_visitor(self) -> TreeVisitor[any, any]:
        return self.visitor
