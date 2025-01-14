from typing import Optional

from rewrite import Cursor
from rewrite import Tree
from rewrite.java import Space, Literal, Identifier, JRightPadded, JLeftPadded, Modifier
from rewrite.python import PythonVisitor
from rewrite.visitor import T, P


class TreeVisitingPrinter(PythonVisitor):
    INDENT = "  "
    ELEMENT_PREFIX = "\\---"
    CONTINUE_PREFIX = "|---"
    UNVISITED_PREFIX = "#"
    BRANCH_CONTINUE_CHAR = '|'
    BRANCH_END_CHAR = '\\'
    CONTENT_MAX_LENGTH = 120

    _last_cursor_stack = []
    _lines = []

    def __init__(self, indent: str = "  "):
        super().__init__()
        self.INDENT = indent

    def visit(self, tree: Optional[Tree], p: P, parent: Optional[Cursor] = None) -> Optional[T]:
        if tree is None:
            return super().visit(None, p, parent)  # pyright: ignore [reportReturnType]

        _current_stack = list(self._cursor.get_path())
        _current_stack.reverse()
        depth = len(_current_stack)
        if not self._last_cursor_stack:
            self._last_cursor_stack = _current_stack + [tree]
        else:
            diff_position = self.find_diff_pos(_current_stack, self._last_cursor_stack)
            if diff_position >= 0:
                for i in _current_stack[diff_position:]:
                    self._lines += [[depth, i]]
                self._last_cursor_stack = self._last_cursor_stack[:diff_position]

        self._lines += [[depth, tree]]
        self._last_cursor_stack = _current_stack + [tree]
        return super().visit(tree, p, parent)  # pyright: ignore [reportReturnType]

    def _print_tree(self) -> str:
        output = ""
        offset = 0
        for idx, (depth, element) in enumerate(self._lines):
            offset = depth if idx == 0 else offset
            padding = self.INDENT * (depth - offset)
            if idx + 1 < len(self._lines) and self._lines[idx + 1][0] <= depth or idx + 1 == len(self._lines):
                output += padding + self.CONTINUE_PREFIX + self._print_element(element) + "\n"
            else:
                output += padding + self.ELEMENT_PREFIX + self._print_element(element) + "\n"
        return output

    def _print_element(self, element) -> str:
        type_name = type(element).__name__
        line = []

        if hasattr(element, "before"):
            line.append(f"before= {self._print_space(element.before)}")

        if hasattr(element, "after"):
            line.append(f"after= {self._print_space(element.after)}")

        if hasattr(element, "suffix"):
            line.append(f"suffix= {self._print_space(element.suffix)}")

        if hasattr(element, "prefix"):
            line.append(f"prefix= {self._print_space(element.prefix)}")

        if isinstance(element, Identifier):
            type_name = f'{type_name} | "{element.simple_name}"'

        if isinstance(element, Literal):
            type_name = f'{type_name} | {element.value_source}'

        if isinstance(element, JRightPadded):
            return f'{type_name} | after= {self._print_space(element.after)}'

        if isinstance(element, JLeftPadded):
            return f'{type_name} | before= {self._print_space(element.before)}'

        if isinstance(element, Modifier):
            return type_name + (
                (" | " + element.type.name) if hasattr(element, "type") else "")

        if line:
            return type_name + " | " + " | ".join(line)
        return type_name

    @staticmethod
    def _print_space(space: Space) -> str:
        parts = []
        if space.whitespace:
            parts.append(f'whitespace="{repr(space.whitespace)}"')
        if space.comments:
            parts.append(f'comments="{space.comments}"')
        return " ".join(parts).replace("\n", "\\s\n")

    @staticmethod
    def print_tree_all(tree: "Tree") -> str:
        visitor = TreeVisitingPrinter()
        visitor.visit(tree, None, None)
        return visitor._print_tree()

    def find_diff_pos(self, cursor_stack, last_cursor_stack):
        diff_pos = -1
        for i in range(len(cursor_stack)):
            if i >= len(last_cursor_stack):
                diff_pos = i
                break
            if cursor_stack[i] != last_cursor_stack[i]:
                diff_pos = i
                break
        return diff_pos
