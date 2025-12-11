"""Analysis router - endpoints for file comparison and analysis."""

from fastapi import APIRouter, File, UploadFile, HTTPException

from deepcsim.core.analyzer import CodeAnalyzer
from deepcsim.core.similarity import SimilarityCalculator
from deepcsim.api.schemas import AnalyzeResponse

router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
):
    """
    Analyze and compare two Python files for similarity.

    Returns detailed function-level comparison metrics.
    """
    try:
        # Read files
        content1 = (await file1.read()).decode("utf-8")
        content2 = (await file2.read()).decode("utf-8")

        # Analyze both files
        analyzer1 = CodeAnalyzer(content1, file1.filename)
        analyzer2 = CodeAnalyzer(content2, file2.filename)

        analyzer1.analyze()
        analyzer2.analyze()

        # Calculate similarities
        comparisons = []
        for fname1, func1 in analyzer1.functions.items():
            for fname2, func2 in analyzer2.functions.items():
                similarity = SimilarityCalculator.calculate_all(func1, func2)

                comparisons.append(
                    {
                        "func1_name": fname1,
                        "func2_name": fname2,
                        "func1_source": func1.source,
                        "func2_source": func2.source,
                        "func1_lines": f"{func1.line_start}-{func1.line_end}",
                        "func2_lines": f"{func2.line_start}-{func2.line_end}",
                        "similarity": similarity,
                    }
                )

        # Calculate statistics
        composite_scores = [
            c["similarity"]["composite"] for c in comparisons
        ]
        avg_similarity = (
            sum(composite_scores) / len(composite_scores)
            if composite_scores
            else 0
        )
        high_similarity_count = sum(
            1 for score in composite_scores if score >= 80
        )

        return {
            "file1_name": file1.filename,
            "file2_name": file2.filename,
            "file1_functions": len(analyzer1.functions),
            "file2_functions": len(analyzer2.functions),
            "comparisons": comparisons,
            "avg_similarity": avg_similarity,
            "high_similarity_count": high_similarity_count,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
