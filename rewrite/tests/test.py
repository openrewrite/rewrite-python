from rewrite.core import random_id
from rewrite.core.marker import Markers
import rewrite.properties.tree as py

f = py.File(
    id=random_id(),
    prefix='',
    markers=Markers.EMPTY,
    source_path='tree.py'
)

print(f)
print(f.with_prefix(' ') is f)
print(f.with_prefix(' ') == f)
print(f.with_prefix('') is f)
print(f.with_prefix(' ').with_prefix('') == f) # value equality
print(f.with_prefix(' ').with_prefix('') is f) # referential equality