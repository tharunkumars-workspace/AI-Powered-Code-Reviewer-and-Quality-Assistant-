import ast

class CodeParser:
    def __init__(self, source_code):
        self.source_code = source_code
        self.tree = None

    def parse(self):
        self.tree = ast.parse(self.source_code)
        return self.tree

    def extract_details(self):
        functions = []

        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "type": "Function",
                    "start_line": node.lineno,
                    "end_line": node.end_lineno,
                    "has_docstring": ast.get_docstring(node) is not None,
                    "complexity": self.calculate_complexity(node)
                })

        return functions

    def calculate_complexity(self, node):
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.And, ast.Or, ast.Try, ast.ExceptHandler)):
                complexity += 1
        return complexity