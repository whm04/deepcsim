"""File and Explorer schemas."""

from pydantic import BaseModel, Field
from typing import List


class FileNode(BaseModel):
    """Represents a file or directory in the file tree."""

    name: str = Field(..., description="Name of the file or directory")
    path: str = Field(..., description="Relative path from root")
    isDirectory: bool = Field(..., description="Whether this is a directory")
    type: str = Field(
        ..., description="File type (python, text, binary, etc.)"
    )

    class Config:
        schema_extra = {
            "example": {
                "name": "module.py",
                "path": "src/module.py",
                "isDirectory": False,
                "type": "python",
            }
        }


class FileInfoRequest(BaseModel):
    """Request body for file information endpoint."""

    path: str = Field(..., description="Path to the file or directory")

    class Config:
        schema_extra = {"example": {"path": "src/deepcsim/core/analyzer.py"}}


class FileInfoResponse(BaseModel):
    """Response for file information including similar files."""

    name: str = Field(..., description="File name")
    path: str = Field(..., description="Relative path")
    type: str = Field(..., description="File type")
    isDirectory: bool = Field(..., description="Is directory")
    size: int = Field(..., description="File size in bytes")
    created: float = Field(..., description="Creation timestamp")
    modified: float = Field(..., description="Modification timestamp")
    similar_files: List[dict] = Field(
        default_factory=list, description="List of similar files"
    )

    class Config:
        schema_extra = {
            "example": {
                "name": "analyzer.py",
                "path": "src/deepcsim/core/analyzer.py",
                "type": "python",
                "isDirectory": False,
                "size": 2048,
                "created": 1699000000.0,
                "modified": 1699000000.0,
                "similar_files": [],
            }
        }
