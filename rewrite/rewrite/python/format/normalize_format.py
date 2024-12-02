from __future__ import annotations

from typing import cast, Optional, TypeVar

from rewrite import Tree, P, Cursor
from rewrite.java import MethodDeclaration, J, Space, ClassDeclaration
from rewrite.python import PythonVisitor, PyComment
from rewrite.visitor import T

J2 = TypeVar('J2', bound=J)


class NormalizeFormatVisitor(PythonVisitor):
    def __init__(self, stop_after: Tree = None):
        self._stop_after = stop_after
        self._stop = False

    def visit_class_declaration(self, cd: ClassDeclaration, p: P) -> J:
        cd: ClassDeclaration = cast(ClassDeclaration, super().visit_class_declaration(cd, p))
        if cd.leading_annotations:
            cd = _concatenate_prefix(cd, Space.first_prefix(cd.leading_annotations))
            cd = cd.with_leading_annotations(Space.format_first_prefix(cd.leading_annotations, Space.EMPTY))
            return cd

        cd = _concatenate_prefix(cd, cd.padding.kind.prefix)
        cd = cd.padding.with_kind(cd.padding.kind.with_prefix(Space.EMPTY))
        return cd

    def visit_method_declaration(self, md: MethodDeclaration, p: P) -> J:
        md: MethodDeclaration = cast(MethodDeclaration, super().visit_method_declaration(md, p))
        if md.leading_annotations:
            md = _concatenate_prefix(md, Space.first_prefix(md.leading_annotations))
            md = md.with_leading_annotations(Space.format_first_prefix(md.leading_annotations, Space.EMPTY))
            return md

        if md.modifiers:
            md = _concatenate_prefix(md, Space.first_prefix(md.modifiers))
            md = md.with_modifiers(Space.format_first_prefix(md.modifiers, Space.EMPTY))
            return md

        return md

    def post_visit(self, tree: T, p: P) -> Optional[T]:
        if self._stop_after and tree == self._stop_after:
            self._stop = True
        return tree

    def visit(self, tree: Optional[Tree], p: P, parent: Optional[Cursor] = None) -> Optional[T]:
        return tree if self._stop else super().visit(tree, p, parent)


def _common_margin(s1, s2):
    if s1 is None:
        s = str(s2)
        return s[s.rfind('\n') + 1:]

    min_length = min(len(s1), len(s2))
    for i in range(min_length):
        if s1[i] != s2[i] or not s1[i].isspace():
            return s1[:i]

    return s2 if len(s2) < len(s1) else s1


def _concatenate_prefix(j: J, prefix: Space) -> J2:
    shift = _common_margin(None, j.prefix.whitespace)

    def modify_comment(c: PyComment):
        if len(shift) == 0:
            return c
        c = c.with_text(c.text.replace('\n', '\n' + shift))
        if '\n' in c.suffix:
            c = c.with_suffix(c.suffix.replace('\n', '\n' + shift))
        return c

    comments = j.prefix.comments + \
               [modify_comment(cast(PyComment, comment)) for comment in prefix.comments]

    new_prefix = j.prefix
    new_prefix = new_prefix.with_whitespace(new_prefix.whitespace + prefix.whitespace)
    new_prefix = new_prefix.with_comments(comments)

    return j.with_prefix(new_prefix)
