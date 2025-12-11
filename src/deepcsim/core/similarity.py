from typing import Dict
from .metrics import FunctionMetrics

class SimilarityCalculator:
    @staticmethod
    def calculate_structural(func1: FunctionMetrics, func2: FunctionMetrics) -> float:
        if func1.ast_hash == func2.ast_hash:
            return 100.0
        
        all_node_types = set(func1.node_types.keys()) | set(func2.node_types.keys())
        if not all_node_types:
            return 0.0
        
        similarity = 0.0
        for node_type in all_node_types:
            count1 = func1.node_types.get(node_type, 0)
            count2 = func2.node_types.get(node_type, 0)
            max_count = max(count1, count2)
            if max_count > 0:
                similarity += (1 - abs(count1 - count2) / max_count)
        
        return (similarity / len(all_node_types)) * 100
    
    @staticmethod
    def calculate_semantic(func1: FunctionMetrics, func2: FunctionMetrics) -> float:
        calls_union = func1.called_functions | func2.called_functions
        calls_intersection = func1.called_functions & func2.called_functions
        calls_sim = (len(calls_intersection) / len(calls_union) * 100) if calls_union else 100.0
        
        var_count_diff = abs(len(func1.variables_used) - len(func2.variables_used))
        max_vars = max(len(func1.variables_used), len(func2.variables_used))
        vars_sim = ((1 - var_count_diff / max_vars) * 100) if max_vars > 0 else 100.0
        
        return (calls_sim * 0.7 + vars_sim * 0.3)
    
    @staticmethod
    def calculate_metric(func1: FunctionMetrics, func2: FunctionMetrics) -> float:
        metrics = [
            ('num_statements', 1.0),
            ('num_args', 2.0),
            ('cyclomatic_complexity', 2.0),
            ('nesting_depth', 1.5)
        ]
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for metric_name, weight in metrics:
            val1 = getattr(func1, metric_name)
            val2 = getattr(func2, metric_name)
            max_val = max(val1, val2)
            
            if max_val > 0:
                metric_sim = (1 - abs(val1 - val2) / max_val) * 100
                weighted_sum += metric_sim * weight
                total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    @classmethod
    def calculate_all(cls, func1: FunctionMetrics, func2: FunctionMetrics) -> Dict[str, float]:
        structural = cls.calculate_structural(func1, func2)
        semantic = cls.calculate_semantic(func1, func2)
        metric = cls.calculate_metric(func1, func2)
        composite = (structural * 0.5 + semantic * 0.3 + metric * 0.2)
        
        return {
            'structural': round(structural, 2),
            'semantic': round(semantic, 2),
            'metric': round(metric, 2),
            'composite': round(composite, 2)
        }
