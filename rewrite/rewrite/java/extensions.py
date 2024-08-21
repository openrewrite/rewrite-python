from typing import Optional, TypeVar, TYPE_CHECKING

from .support_types import J, JRightPadded, JLeftPadded, JContainer, Space

if TYPE_CHECKING:
    from ..visitor import JavaVisitor
    from .tree import *

T = TypeVar('T')
J2 = TypeVar('J2', bound=J)


def visit_container(v: 'JavaVisitor', container: Optional[JContainer[J2]], loc: JContainer.Location, p) -> Optional[JContainer[J2]]:
    if container is None:
        return None

    v.cursor = Cursor(v.cursor, container)
    before = v.visit_space(container.before, loc.before_location, p)
    js = [v.visit_right_padded(el.element, loc.element_location, p) for el in container.padding.elements]
    v.cursor = v.cursor.parent

    return container if js == container.padding.elements and before is container.before else JContainer(before, js, container.markers)


def visit_right_padded(v: 'JavaVisitor', right: Optional[JRightPadded[T]], loc: JRightPadded.Location, p) -> Optional[JRightPadded[T]]:
    if right is None:
        return None

    t = right.element
    v.cursor = Cursor(v.cursor, right)
    t = v.visit_and_cast(t, T, p)
    v.cursor = v.cursor.parent

    if t is None:
        return None

    right = right.with_element(t)
    right = right.with_after(v.visit_space(right.after, loc, p))
    right = right.with_markers(v.visit_markers(right.markers, p))
    return right


def visit_left_padded(v: 'JavaVisitor', left: Optional[JLeftPadded[T]], loc: JLeftPadded.Location, p) -> Optional[JLeftPadded[T]]:
    if left is None:
        return None

    v.cursor = Cursor(v.cursor, left)
    before = v.visit_space(left.before, loc.before_location, p)
    t = left.element
    if isinstance(t, Tree):
        t = v.visit_and_cast(t, T, p)
    v.cursor = v.cursor.parent

    if left.element is t and before is left.before:
        return left
    elif t is None:
        return None

    return JLeftPadded(before, t, left.markers)


def visit_space(v: 'JavaVisitor', space: Optional[Space], loc: Space.Location, p):
    # FIXME support Javadoc
    return space


def with_name(method: 'MethodInvocation', name: 'Identifier') -> 'MethodInvocation':
    # FIXME add type attribution logic
    return method if name is method.name else replace(method, _name=name)
