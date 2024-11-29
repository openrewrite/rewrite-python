from typing import cast, Optional, TypeVar

from rewrite import Tree, P, Cursor
from rewrite.java import MethodDeclaration, J, Space
from rewrite.python import PythonVisitor, PyComment
from rewrite.visitor import T


J2 = TypeVar('J2', bound=J)


def common_margin(s1, s2):
    if s1 is None:
        s = str(s2)
        return s[s.rfind('\n') + 1:]

    min_length = min(len(s1), len(s2))
    for i in range(min_length):
        if s1[i] != s2[i] or not s1[i].isspace():
            return s1[:i]

    return s2 if len(s2) < len(s1) else s1


class NormalizeFormatVisitor(PythonVisitor):
    def __init__(self, stop_after: Tree = None):
        self._stop_after = stop_after
        self._stop = False

    def visit_method_declaration(self, md: MethodDeclaration, p: P) -> J:
        md: MethodDeclaration = cast(MethodDeclaration, super().visit_method_declaration(md, p))
        if md.leading_annotations:
            md = self.concatenate_prefix(md, Space.first_prefix(md.leading_annotations))
        return md

    def post_visit(self, tree: T, p: P) -> Optional[T]:
        if self._stop_after and tree == self._stop_after:
            self._stop = True
        return tree

    def visit(self, tree: Optional[Tree], p: P, parent: Optional[Cursor] = None) -> Optional[T]:
        return tree if self._stop else super().visit(tree, p, parent)

    def concatenate_prefix(self, j: J2, prefix: Space) -> J2:
        shift = common_margin(None, j.prefix.whitespace)

        def modify_comment(c: PyComment):
            if len(shift) == 0:
                return c
            c = c.with_text(c.text.replace('\n', '\n' + shift))
            if '\n' in c.suffix:
                c = c.with_suffix(c.suffix.replace('\n', '\n' + shift))
            return c

        comments = j.prefix.comments + \
            [modify_comment(cast(PyComment, comment)) for comment in prefix.comments]

        new_prefix = j.get_prefix()
        new_prefix = new_prefix.with_whitespace(new_prefix.whitespace + prefix.whitespace)
        new_prefix = new_prefix.with_comments(comments)

        return j.with_prefix(new_prefix)
