from rewrite.core import random_id
from rewrite.core.marker import Markers
from rewrite.properties.tree import File

f = File(
    id=random_id(),
    prefix='test',
    markers=Markers.EMPTY,
    sourcePath='tree.py'
)

print(f)