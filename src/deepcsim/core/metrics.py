from dataclasses import dataclass, field
from typing import Dict, Set

@dataclass
class FunctionMetrics:
    name: str
    source: str
    line_start: int
    line_end: int
    num_statements: int = 0
    num_args: int = 0
    cyclomatic_complexity: int = 1
    nesting_depth: int = 0
    node_types: Dict[str, int] = field(default_factory=dict)
    called_functions: Set[str] = field(default_factory=set)
    variables_used: Set[str] = field(default_factory=set)
    ast_hash: str = ""
