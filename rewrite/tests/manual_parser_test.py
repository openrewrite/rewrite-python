import io
import pathlib
import socket
import sys

from rewrite import InMemoryExecutionContext, ParserInput, ParseError, ParseExceptionResult
from rewrite.python import PythonParser

path = sys.argv[1] if len(sys.argv) > 1 else '/Users/knut/git/moderneinc/moderne-cli/working-set/face-alignment/examples/detect_landmarks_in_image.py'

from rewrite_remote import RemotingContext, RemotePrinterFactory
from rewrite_remote.server import register_remoting_factories

remoting_context = RemotingContext()
register_remoting_factories()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 65432))
remoting_context.connect(s)
RemotePrinterFactory(remoting_context.client).set_current()
remoting_context.client.reset()

parser = PythonParser(None)
res = parser.parse_inputs([ParserInput(pathlib.Path(path), None, False, lambda: open(path, 'r', newline='', encoding='utf-8'))], relative_to=None, ctx=InMemoryExecutionContext())
for r in res:
    if isinstance(r, ParseError):
        print(r.markers.find_first(ParseExceptionResult).message)
