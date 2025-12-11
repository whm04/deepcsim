import ast
import hashlib
from collections import defaultdict
from typing import Dict
from .metrics import FunctionMetrics

class ASTAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.current_depth = 0
        self.max_depth = 0
        self.complexity = 1
        self.node_counts = defaultdict(int)
        self.function_calls = set()
        self.variables = set()
    
    def visit(self, node):
        self.node_counts[type(node).__name__] += 1
        return super().visit(node)
    
    def visit_If(self, node):
        self.complexity += 1
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1
    
    def visit_While(self, node):
        self.complexity += 1
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1
    
    def visit_For(self, node):
        self.complexity += 1
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1
    
    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.function_calls.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.function_calls.add(node.func.attr)
        self.generic_visit(node)
    
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.variables.add(node.id)
        self.generic_visit(node)


class CodeAnalyzer:
    def __init__(self, source: str, filename: str):
        self.source = source
        self.filename = filename
        self.functions: Dict[str, FunctionMetrics] = {}
        self.lines = source.split('\n')
    
    def analyze(self):
        try:
            tree = ast.parse(self.source, filename=self.filename)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    metrics = self._extract_metrics(node)
                    self.functions[node.name] = metrics
        except SyntaxError as e:
            raise ValueError(f"Syntax error: {e}")
    
    def _extract_metrics(self, func_node: ast.FunctionDef) -> FunctionMetrics:
        func_source = ast.get_source_segment(self.source, func_node)
        analyzer = ASTAnalyzer()
        analyzer.visit(func_node)
        
        num_args = len(func_node.args.args)
        num_statements = len([n for n in ast.walk(func_node) if isinstance(n, ast.stmt)]) - 1
        
        ast_structure = self._get_ast_structure(func_node)
        ast_hash = hashlib.md5(ast_structure.encode()).hexdigest()
        
        return FunctionMetrics(
            name=func_node.name,
            source=func_source or "",
            line_start=func_node.lineno,
            line_end=func_node.end_lineno or func_node.lineno,
            num_statements=num_statements,
            num_args=num_args,
            cyclomatic_complexity=analyzer.complexity,
            nesting_depth=analyzer.max_depth,
            node_types=dict(analyzer.node_counts),
            called_functions=analyzer.function_calls,
            variables_used=analyzer.variables,
            ast_hash=ast_hash
        )
    
    def _get_ast_structure(self, node: ast.AST) -> str:
        if isinstance(node, ast.AST):
            fields = []
            for field, value in ast.iter_fields(node):
                if field in ('name', 'id', 'arg', 's', 'n'):
                    continue
                if isinstance(value, list):
                    fields.append(f"{field}:[{','.join(self._get_ast_structure(item) for item in value)}]")
                else:
                    fields.append(f"{field}:{self._get_ast_structure(value)}")
            return f"{node.__class__.__name__}({','.join(fields)})"
        return ""
