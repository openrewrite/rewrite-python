import io
import pathlib
import socket
import sys

from rewrite import InMemoryExecutionContext, ParserInput, ParseError, ParseExceptionResult
from rewrite.python import PythonParser

path = sys.argv[1] if len(sys.argv) > 1 else '../../../../pydantic/pydantic/pydantic/_internal/_known_annotated_metadata.py'

from rewrite.remote import RemotingContext, RemotePrinterFactory
from rewrite.remote.server import register_remoting_factories

remoting_context = RemotingContext()
register_remoting_factories()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 65432))
remoting_context.connect(s)
RemotePrinterFactory(remoting_context.client).set_current()
remoting_context.client.reset()

parser = PythonParser()
with open(path, 'r', encoding='utf-8') as file:
    res = parser.parse_inputs([ParserInput(pathlib.Path(path), None, False, lambda: file)], relative_to=None, ctx=InMemoryExecutionContext())
    for r in res:
        if isinstance(r, ParseError):
            print(r.markers.find_first(ParseExceptionResult).exception_message)
