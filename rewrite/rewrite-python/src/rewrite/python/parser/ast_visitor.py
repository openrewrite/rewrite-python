import ast


class SimpleASTVisitor(ast.NodeVisitor):
    def visit_FunctionDef(self, node: ast.FunctionDef):
        print(f"Visiting function: {node.name}")
        self.generic_visit(node)  # Continue visiting child nodes
