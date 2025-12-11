from typing import Optional
from deepcsim.core.analyzer import CodeAnalyzer
from deepcsim.core.similarity import SimilarityCalculator

def compare_source(source1: str, source2: str, filename1: str = "source1", filename2: str = "source2", threshold: float = 0.0) -> dict:
    """
    Compare two source code snippets and return the similarity metrics.
    Returns a result format compatible with scan_directory's 'results' item.
    """
    analyzer1 = CodeAnalyzer(source1, filename1)
    analyzer1.analyze()
    
    analyzer2 = CodeAnalyzer(source2, filename2)
    analyzer2.analyze()
    
    if not analyzer1.functions or not analyzer2.functions:
        return {'count': 0, 'results': []}
        
    pair_comparisons = []
    all_composite_scores = []
    
    for fname1, func1 in analyzer1.functions.items():
        for fname2, func2 in analyzer2.functions.items():
            similarity = SimilarityCalculator.calculate_all(func1, func2)
            score = similarity["composite"]
            all_composite_scores.append(score)
            
            # Include all pairs or filter by threshold if needed. 
            # Since this is a direct comparison, we usually want all unless threshold is strict.
            if score >= threshold:
                pair_comparisons.append({
                    'func1_name': fname1,
                    'func2_name': fname2,
                    'func1_source': func1.source,
                    'func2_source': func2.source,
                    'func1_lines': f"{func1.line_start}-{func1.line_end}",
                    'func2_lines': f"{func2.line_start}-{func2.line_end}",
                    'similarity': similarity
                })
                
    if not all_composite_scores:
        return {'count': 0, 'results': []}
        
    max_score = max(all_composite_scores) if all_composite_scores else 0.0
    avg_similarity = sum(all_composite_scores) / len(all_composite_scores) if all_composite_scores else 0.0
    high_similarity_count = sum(1 for score in all_composite_scores if score >= 80)
    
    result_item = {
        "file1": filename1,
        "file2": filename2,
        "file1_functions": len(analyzer1.functions),
        "file2_functions": len(analyzer2.functions),
        "comparisons": sorted(pair_comparisons, key=lambda x: x['similarity']['composite'], reverse=True),
        "avg_similarity": round(avg_similarity, 2),
        "high_similarity_count": high_similarity_count,
        "similarity": round(max_score, 2),
        "reason": "High function-level similarity"
    }
    
    return {'count': 1, 'results': [result_item]}
