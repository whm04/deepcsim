import os
import hashlib
from itertools import combinations
from typing import Dict, List, Any

from deepcsim.core.analyzer import CodeAnalyzer
from deepcsim.core.similarity import SimilarityCalculator
from deepcsim.constants import is_ignored


def scan_directory(directory: str, threshold: float = 80.0) -> Dict[str, Any]:
    """
    Recursively scan a directory, analyze all Python files,
    and detect highly similar files based on AST structure.
    """
    if not os.path.exists(directory):
        raise ValueError("Directory does not exist")

    file_reports = {}
    print("Starting directory scan...", directory)
    # 1. Scan all folders
    for root, dirs, files in os.walk(directory):
        # Remove virtual environment directories from traversal
        dirs[:] = [d for d in dirs if not is_ignored(d)]

        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        src = f.read()
                except Exception:
                    continue

                # Skip empty files
                if not src.strip():
                    continue

                analyzer = CodeAnalyzer(src, full_path)
                try:
                    analyzer.analyze()
                except Exception:
                    continue

                # Compute file-level AST hash (combine all function AST hashes)
                if not analyzer.functions:
                    pass

                file_hash = hashlib.md5(
                    "".join(
                        m.ast_hash for m in analyzer.functions.values()).encode()
                ).hexdigest()

                file_reports[full_path] = {
                    "functions": analyzer.functions,
                    "file_hash": file_hash,
                }

    # 2. Compare files pairwise
    similar_pairs = []

    for file1, file2 in combinations(file_reports.keys(), 2):
        f1 = file_reports[file1]
        f2 = file_reports[file2]

        # Compare function by function
        pair_comparisons = []
        all_composite_scores = []

        for fname1, func1 in f1["functions"].items():
            for fname2, func2 in f2["functions"].items():
                similarity = SimilarityCalculator.calculate_all(func1, func2)
                score = similarity["composite"]
                all_composite_scores.append(score)

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
            continue

        max_score = max(all_composite_scores)

        # Check if files are identical by hash for reporting
        is_identical = f1["file_hash"] == f2["file_hash"]

        # Filter by threshold (or if identical)
        if max_score >= threshold or is_identical:
            avg_similarity = sum(all_composite_scores) / \
                len(all_composite_scores)
            high_similarity_count = sum(
                1 for score in all_composite_scores if score >= 80)

            similar_pairs.append({
                "file1": file1,
                "file2": file2,
                "file1_functions": len(f1["functions"]),
                "file2_functions": len(f2["functions"]),
                "comparisons": pair_comparisons,
                "avg_similarity": avg_similarity,
                "high_similarity_count": high_similarity_count,
                "similarity": round(max_score, 2),
                "reason": "Identical AST structure" if is_identical else "High function-level similarity"
            })

    return {"count": len(similar_pairs), "results": similar_pairs}


def find_matches_for_file(target_path: str, directory: str, threshold: float = 50.0) -> List[Dict[str, Any]]:
    """
    Find files in directory that are similar to the target file.
    Returns a list of matches with detailed function comparisons.
    """
    if not os.path.exists(target_path):
        raise ValueError(f"Target file not found: {target_path}")

    try:
        with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
            target_src = f.read()
    except Exception as e:
        raise ValueError(f"Could not read target file: {e}")

    target_analyzer = CodeAnalyzer(target_src, target_path)
    target_analyzer.analyze()

    if not target_analyzer.functions:
        return []

    target_hash = hashlib.md5(
        "".join(m.ast_hash for m in target_analyzer.functions.values()).encode()
    ).hexdigest()

    matches = []

    # Scan all folders
    for root, dirs, files in os.walk(directory):
        # Remove virtual environment directories from traversal
        dirs[:] = [d for d in dirs if not is_ignored(d)]

        for file in files:
            if not file.endswith(".py"):
                continue

            full_path = os.path.join(root, file)

            # Skip the target file itself
            if os.path.abspath(full_path) == os.path.abspath(target_path):
                continue

            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    src = f.read()
            except Exception:
                continue

            if not src.strip():
                continue

            analyzer = CodeAnalyzer(src, full_path)
            try:
                analyzer.analyze()
            except Exception:
                continue

            if not analyzer.functions:
                continue

            # Check for identical files first
            file_hash = hashlib.md5(
                "".join(m.ast_hash for m in analyzer.functions.values()).encode()
            ).hexdigest()

            is_identical = target_hash == file_hash

            # Compare function by function
            pair_comparisons = []
            all_composite_scores = []

            for fname1, func1 in target_analyzer.functions.items():
                for fname2, func2 in analyzer.functions.items():
                    similarity = SimilarityCalculator.calculate_all(
                        func1, func2)
                    score = similarity["composite"]

                    if score >= threshold:  # Only pairs meeting threshold
                        all_composite_scores.append(score)
                        pair_comparisons.append({
                            'func1_name': fname1,
                            'func2_name': fname2,
                            'func1_source': func1.source,
                            'func2_source': func2.source,
                            'func1_lines': f"{func1.line_start}-{func1.line_end}",
                            'func2_lines': f"{func2.line_start}-{func2.line_end}",
                            'similarity': similarity
                        })

            if not all_composite_scores and not is_identical:
                continue

            max_score = max(
                all_composite_scores) if all_composite_scores else 0.0

            if max_score >= threshold or is_identical:
                avg_similarity = sum(
                    all_composite_scores) / len(all_composite_scores) if all_composite_scores else 0
                high_similarity_count = sum(
                    1 for score in all_composite_scores if score >= 80)

                matches.append({
                    "file": full_path,
                    "relative_path": os.path.relpath(full_path, directory).replace("\\", "/"),
                    "similarity": 100.0 if is_identical else round(max_score, 2),
                    "avg_similarity": round(avg_similarity, 2),
                    "high_similarity_count": high_similarity_count,
                    "reason": "Identical AST usage" if is_identical else "High function similarity",
                    "comparisons": sorted(pair_comparisons, key=lambda x: x['similarity']['composite'], reverse=True)
                })

    # Sort matches by max similarity
    matches.sort(key=lambda x: x['similarity'], reverse=True)
    return matches
