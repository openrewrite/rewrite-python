from __future__ import annotations

import socket
import textwrap
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Optional, Callable, Iterable, List, TypeVar, Any, cast
from uuid import UUID

from rewrite import InMemoryExecutionContext, ParserInput, ParserBuilder, random_id, ParseError, ParseExceptionResult, \
    ExecutionContext, Recipe, TreeVisitor, SourceFile, PrintOutputCapture
from rewrite.execution import InMemoryLargeSourceSet
from rewrite.python import CompilationUnit
from rewrite.python.parser import PythonParserBuilder
from rewrite.python.printer import PythonPrinter

S = TypeVar('S', bound=SourceFile)

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

    _after_recipe: Optional[Callable[[S], None]] = lambda _: None

    @property
    def after_recipe(self) -> Optional[Callable[[S], None]]:
        return self._after_recipe


@dataclass(frozen=True)
class CompositeRecipe(Recipe):
    recipes: Iterable[Recipe]

    def get_recipe_list(self) -> List[Recipe]:
        return list(self.recipes)


@dataclass(frozen=True, eq=False)
class RecipeSpec:
    _recipe: Optional[Recipe] = None

    @property
    def recipe(self) -> Optional[Recipe]:
        return self._recipe

    def with_recipe(self, recipe: Recipe) -> RecipeSpec:
        return self if recipe is self._recipe else RecipeSpec(recipe)

    def with_recipes(self, *recipes: Recipe) -> RecipeSpec:
        return RecipeSpec(CompositeRecipe(recipes))

    _parsers: Iterable[ParserBuilder] = field(default_factory=list)

    @property
    def parsers(self) -> Iterable[ParserBuilder]:
        return self._parsers

    def with_parsers(self, parsers: Iterable[ParserBuilder]) -> RecipeSpec:
        return self if parsers is self._parsers else RecipeSpec(self._recipe, parsers)

def rewrite_run(*source_specs: Iterable[SourceSpec], spec: Optional[RecipeSpec] = None) -> None:
    USE_REMOTE = False

    if USE_REMOTE:
        from rewrite_remote import RemotingContext, RemotePrinterFactory
        from rewrite_remote.server import register_remoting_factories
        remoting_context = RemotingContext()
        register_remoting_factories()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # if USE_REMOTE:
        s.connect(('localhost', 65432))
        remoting_context.connect(s)
        RemotePrinterFactory(remoting_context.client).set_current()

    try:
        ctx = InMemoryExecutionContext()
        ctx.put_message(ExecutionContext.REQUIRE_PRINT_EQUALS_INPUT, False)

        configured_parsers = {p.source_file_type: p for p in spec.parsers} if spec else {}
        parsers = {s.parser.source_file_type: configured_parsers.get(s.parser.source_file_type, s.parser) for source_spec in source_specs for s in source_spec}

        spec_by_source_file = {}
        for source in source_specs:
            for source_spec in source:
                parser = parsers[source_spec.parser.source_file_type].build()
                source_path = source_spec.source_path if source_spec.source_path \
                    else parser.source_path_from_source_text(Path('.'), source_spec.before)
                for source_file in parser.parse_inputs(
                        [ParserInput(source_path, None, True, lambda: StringIO(source_spec.before))], None, ctx):
                    if isinstance(source_file, ParseError):
                        assert False, f'Parser threw an exception:\n%{source_file.markers.find_first(ParseExceptionResult).message}'  # type: ignore

                    if USE_REMOTE:
                        remoting_context.reset()
                        remoting_context.client.reset()

                    assert source_file.print_all() == source_spec.before

                    spec_by_source_file[source_file] = source_spec

        if spec and spec.recipe:
            recipe = spec.recipe
            before = InMemoryLargeSourceSet(list(spec_by_source_file.keys()))
            result = recipe.run(before, ctx)
            for res in result:
                if res._before and res._after:
                    source_spec = spec_by_source_file[res._before]
                    source_spec.after_recipe(res._after)
                    after_printed = res._after.print_all()
                    if source_spec.after is not None:
                        after = source_spec.after(after_printed)
                        assert after_printed == after
                    else:
                        assert after_printed == source_spec.before
        else:
            for before_source in spec_by_source_file.keys():
                source_spec = spec_by_source_file[before_source]
                if source_spec.after_recipe is not None:
                    source_spec.after_recipe(before_source)

    except Exception:
        raise
    finally:
        if USE_REMOTE:
            remoting_context.close()


def python(before: str, after: Optional[str] = None, after_recipe: Optional[Callable[[CompilationUnit], None]] = lambda s: None) -> list[SourceSpec]:
    return [SourceSpec(
        random_id(),
        PythonParserBuilder(),
        textwrap.dedent(before),
        None if after is None else lambda _: textwrap.dedent(after),
        None,
        cast(Optional[Callable[[S], None]], after_recipe)
    )]


def from_visitor(visitor: TreeVisitor[Any, Any]) -> Recipe:
    return AdHocRecipe(visitor)


@dataclass(frozen=True)
class AdHocRecipe(Recipe):
    visitor: TreeVisitor[Any, Any]

    def get_visitor(self) -> TreeVisitor[Any, Any]:
        return self.visitor
