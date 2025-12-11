"""Project scan and similarity detection schemas."""

from pydantic import BaseModel, Field
from typing import List


class SimilarFilePair(BaseModel):
    """Represents a pair of similar files."""

    file1: str = Field(..., description="Path to first file")
    file2: str = Field(..., description="Path to second file")
    similarity: float = Field(..., description="Similarity score (0-100)")
    reason: str = Field(..., description="Reason for similarity match")

    class Config:
        schema_extra = {
            "example": {
                "file1": "src/module1.py",
                "file2": "src/module2.py",
                "similarity": 92.5,
                "reason": "High function-level similarity",
            }
        }


class ScanProjectRequest(BaseModel):
    """Request body for project scan endpoint."""

    directory: str = Field(..., description="Directory to scan")
    threshold: float = Field(
        default=80.0,
        ge=0,
        le=100,
        description="Similarity threshold percentage",
    )

    class Config:
        schema_extra = {
            "example": {
                "directory": "/path/to/project",
                "threshold": 80.0,
            }
        }


class ScanProjectResponse(BaseModel):
    """Response from project scan endpoint."""

    count: int = Field(..., description="Number of similar file pairs found")
    results: List[SimilarFilePair] = Field(
        ..., description="List of similar file pairs"
    )

    class Config:
        schema_extra = {
            "example": {
                "count": 2,
                "results": [
                    {
                        "file1": "src/module1.py",
                        "file2": "src/module2.py",
                        "similarity": 92.5,
                        "reason": "High function-level similarity",
                    }
                ],
            }
        }
