from __future__ import annotations

from typing import Optional, TypeVar, Union, cast

from rewrite import Tree, P, Cursor, list_map, Marker
from rewrite.java import J, Space, Comment, TextComment, TrailingComma
from rewrite.python import PythonVisitor, PySpace, GeneralFormatStyle, PyComment
from rewrite.visitor import T

J2 = TypeVar('J2', bound=J)


class NormalizeLineBreaksVisitor(PythonVisitor):
    def __init__(self, style: GeneralFormatStyle, stop_after: Tree = None):
        self._stop_after = stop_after
        self._stop = False
        self._style = style

    def visit_space(self, space: Optional[Space], loc: Optional[Union[PySpace.Location, Space.Location]],
                    p: P) -> Space:
        if not space or space is Space.EMPTY or not space.whitespace:
            return space
        s = space.with_whitespace(_normalize_new_lines(space.whitespace, self._style.use_crlf_new_lines))

        def process_comment(comment: Comment) -> Comment:
            if comment.multiline:
                if isinstance(comment, PyComment):
                    comment = comment.with_suffix(_normalize_new_lines(comment.suffix, self._style.use_crlf_new_lines))
                    # TODO: Call PyComment Visitor, but this is not implemented yet....
                    return comment
                elif isinstance(comment, TextComment):
                    comment = comment.with_text(_normalize_new_lines(comment.text, self._style.use_crlf_new_lines))

            return comment.with_suffix(_normalize_new_lines(comment.suffix, self._style.use_crlf_new_lines))

        return s.with_comments(list_map(process_comment, s.comments))

    def post_visit(self, tree: T, _: object) -> Optional[T]:
        if self._stop_after and tree == self._stop_after:
            self._stop = True
        return tree

    def visit(self, tree: Optional[Tree], p: P, parent: Optional[Cursor] = None) -> Optional[T]:
        return tree if self._stop else super().visit(tree, p, parent)

    def visit_marker(self, marker: Marker, p: P) -> Marker:
        m = cast(Marker, super().visit_marker(marker, p))
        if isinstance(m, TrailingComma):
            return m.with_suffix(self.visit_space(m.suffix, None, p))
        return m


STR = TypeVar('STR', bound=Optional[str])


def _normalize_new_lines(text: STR, use_crlf: bool) -> STR:
    """
    Normalize the line breaks in the given text to either use of CRLF or LF.

    :param text: The text to normalize.
    :param use_crlf: Whether to use CRLF line breaks.
    :return: The text with normalized line breaks.
    """
    if text is None or '\n' not in text:
        return text

    normalized = []
    for i, c in enumerate(text):
        if use_crlf and c == '\n' and (i == 0 or text[i - 1] != '\r'):
            normalized.append('\r\n')
        elif use_crlf or c != '\r':
            normalized.append(c)
    return ''.join(normalized)
