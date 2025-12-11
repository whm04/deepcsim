"""Analysis and comparison schemas."""

from pydantic import BaseModel, Field
from typing import List, Dict, Any


class ComparisonResult(BaseModel):
    """Result of comparing two functions."""

    func1_name: str = Field(..., description="Name of first function")
    func2_name: str = Field(..., description="Name of second function")
    func1_source: str = Field(..., description="Source code of first function")
    func2_source: str = Field(
        ..., description="Source code of second function"
    )
    func1_lines: str = Field(..., description="Line range of first function")
    func2_lines: str = Field(..., description="Line range of second function")
    similarity: Dict[str, Any] = Field(
        ..., description="Similarity metrics (structural, semantic, composite)"
    )

    class Config:
        schema_extra = {
            "example": {
                "func1_name": "calculate",
                "func2_name": "compute",
                "func1_source": "def calculate(x): return x * 2",
                "func2_source": "def compute(x): return x * 2",
                "func1_lines": "5-7",
                "func2_lines": "10-12",
                "similarity": {
                    "structural": 95.5,
                    "semantic": 90.0,
                    "composite": 92.75,
                },
            }
        }


class AnalyzeRequest(BaseModel):
    """Request body for file analysis endpoint."""

    # Note: File upload is handled by FastAPI's File and UploadFile
    # This model can be extended if needed


class AnalyzeResponse(BaseModel):
    """Response from analysis endpoint."""

    file1_name: str = Field(..., description="First file name")
    file2_name: str = Field(..., description="Second file name")
    file1_functions: int = Field(
        ..., description="Number of functions in file 1"
    )
    file2_functions: int = Field(
        ..., description="Number of functions in file 2"
    )
    comparisons: List[ComparisonResult] = Field(
        ..., description="Function comparison results"
    )
    avg_similarity: float = Field(..., description="Average similarity score")
    high_similarity_count: int = Field(
        ..., description="Count of high similarity matches (>= 80)"
    )

    class Config:
        schema_extra = {
            "example": {
                "file1_name": "module1.py",
                "file2_name": "module2.py",
                "file1_functions": 5,
                "file2_functions": 5,
                "comparisons": [],
                "avg_similarity": 75.5,
                "high_similarity_count": 2,
            }
        }
