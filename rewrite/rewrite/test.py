import socket
import textwrap
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Optional, Callable
from uuid import UUID

from rewrite import InMemoryExecutionContext, ParserInput, ParserBuilder, random_id, ParseError, ParseExceptionResult, \
    ExecutionContext
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


def rewrite_run(*sources: list[SourceSpec]):
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

        for source in sources:
            for spec in source:
                parser = spec.parser.build()
                source_path = spec.source_path if spec.source_path \
                    else parser.source_path_from_source_text(Path('.'), spec.before)
                for source_file in parser.parse_inputs(
                        [ParserInput(source_path, None, True, lambda: StringIO(spec.before))], None, ctx):
                    if isinstance(source_file, ParseError):
                        assert False, f'Parser threw an exception:\n%{source_file.markers.find_first(ParseExceptionResult).message}'
                    remoting_context.client.reset()
                    assert source_file.print_all() == spec.before

                    if spec.after is not None:
                        after = spec.after(source_file.print_all())
                        assert after == spec.before
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
        None if after is None else lambda: after,
        None
    )]
