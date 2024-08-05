from rewrite.core import random_id
from rewrite.core.marker import Markers
import rewrite.properties.tree as py

f = py.File(
    id=random_id(),
    prefix='test',
    markers=Markers.EMPTY,
    sourcePath='tree.py'
)

print(f)