from __future__ import annotations

from typing import TypeVar

from rewrite import Tree
from rewrite.java import J
from rewrite.python import PythonVisitor, TabsAndIndentsStyle

J2 = TypeVar('J2', bound=J)


class TabsAndIndentsVisitor(PythonVisitor):

    def __init__(self, style: TabsAndIndentsStyle, stop_after: Tree = None):
        self._stop_after = stop_after
        self._style = style
        self._stop = False
