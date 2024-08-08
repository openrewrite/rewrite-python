from typing import Optional, TypeVar

from rewrite.core import Cursor
from rewrite.json.tree.support_types import JsonRightPadded
from rewrite.json.tree.tree import Json
from rewrite.json.visitor import JsonVisitor

T = TypeVar('T', bound=Json)


def visit_right_padded(v: JsonVisitor, right: Optional[JsonRightPadded[T]], p):
    if right is None:
        return None

    t = right.element
    v.cursor = Cursor(v.cursor, right)
    t = v.visit_and_cast(t, T, p)
    v.cursor = v.cursor.parent

    if t is None:
        return None

    right = right.with_element(t)
    right = right.with_after(v.visit_space(right.after, p))
    right = right.with_markers(v.visit_markers(right.markers, p))
    return right
