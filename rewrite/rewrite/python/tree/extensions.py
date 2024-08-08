from typing import Optional, TypeVar

from rewrite.java.tree.support_types import JContainer, JRightPadded, JLeftPadded, Space
from rewrite.java.tree.tree import J
from rewrite.python.tree.support_types import PyContainer, PyRightPadded, PyLeftPadded, PySpace
from rewrite.python.visitor import PythonVisitor


T = TypeVar('T')
J2 = TypeVar('J2', bound=J)


def visit_container(v: PythonVisitor, container: Optional[JContainer[J2]], loc: PyContainer.Location, p) -> Optional[JContainer[J2]]:
    return None


def visit_right_padded(v: PythonVisitor, right: Optional[JRightPadded[T]], loc: PyRightPadded.Location, p) -> Optional[JRightPadded[T]]:
    return None


def visit_left_padded(v: PythonVisitor, left: Optional[JLeftPadded[T]], loc: PyLeftPadded.Location, p) -> Optional[JLeftPadded[T]]:
    return None


def visit_space(v: PythonVisitor, space: Optional[Space], loc: PySpace.Location, p):
    return None
