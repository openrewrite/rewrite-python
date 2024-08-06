from __future__ import annotations

import rewrite.properties.tree as py
from rewrite.core import random_id
from rewrite.core.marker import Markers

f = py.File(
    id=random_id(),
    prefix='',
    markers=Markers.EMPTY,
    source_path='tree.py'
)

assert f is not f.with_prefix(' ')
assert f is f.with_prefix('')
assert f == f.with_prefix(' ')
assert f == f.with_prefix('')
