import pathlib
import socket
import sys

from rewrite import InMemoryExecutionContext
from rewrite.python import PythonParser

file = sys.argv[0] if sys.argv else '../../../../pydantic/pydantic/pydantic/_internal/_known_annotated_metadata.py'

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
res = parser.parse([pathlib.Path(file)], relative_to=None, ctx=InMemoryExecutionContext())
list(res)