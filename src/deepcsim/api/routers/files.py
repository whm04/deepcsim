"""Files router - endpoints for file listing and metadata."""

import os
from fastapi import APIRouter, HTTPException

from deepcsim.core.scanner import find_matches_for_file
from deepcsim.utils.file_info import get_file_type
from deepcsim.constants import is_ignored
from deepcsim.api.schemas import FileInfoRequest, FileInfoResponse

router = APIRouter(prefix="/api", tags=["files"])


@router.get("/files/")
@router.get("/files/{path:path}")
async def list_files(path: str = ""):
    """
    List files and directories from the given path.

    Security: Prevents directory traversal attacks.
    """
    root_dir = os.getcwd()

    # Resolve target directory
    if path:
        target_dir = os.path.abspath(os.path.join(root_dir, path))
    else:
        target_dir = root_dir

    # Security check: prevent directory traversal
    if not target_dir.startswith(root_dir):
        raise HTTPException(status_code=403, detail="Access denied")

    if not os.path.exists(target_dir):
        raise HTTPException(status_code=404, detail="Directory not found")

    if not os.path.isdir(target_dir):
        raise HTTPException(status_code=400, detail="Not a directory")

    children = []
    try:
        with os.scandir(target_dir) as entries:
            for entry in entries:
                # Skip ignored files and directories
                if is_ignored(entry.name):
                    continue

                file_type = get_file_type(entry.name, entry.is_dir())
                rel_path = os.path.relpath(entry.path, root_dir)

                # Normalize path separators to forward slashes
                rel_path = rel_path.replace("\\", "/")

                children.append(
                    {
                        "name": entry.name,
                        "path": rel_path if rel_path != "." else "",
                        "isDirectory": entry.is_dir(),
                        "type": file_type,
                    }
                )

        # Sort: directories first, then files
        children.sort(key=lambda x: (not x["isDirectory"], x["name"].lower()))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "path": path.replace("\\", "/") if path else "",
        "name": os.path.basename(target_dir) if path else "Root",
        "children": children,
    }


@router.post("/file-info/", response_model=FileInfoResponse)
async def get_file_info(request: FileInfoRequest):
    """
    Get detailed information about a specific file or directory.

    Includes metadata and list of similar files (for Python files).
    """
    root_dir = os.getcwd()
    target_path = os.path.abspath(os.path.join(root_dir, request.path))

    # Security check
    if not target_path.startswith(root_dir):
        raise HTTPException(status_code=403, detail="Access denied")

    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail="File not found")

    stats = os.stat(target_path)
    is_dir = os.path.isdir(target_path)
    file_type = get_file_type(target_path, is_dir)

    matches = []
    if file_type == "python":
        try:
            # Find similar files for Python modules
            matches = find_matches_for_file(
                target_path, root_dir, threshold=40.0
            )
        except Exception:
            # Silently skip if matching fails
            pass

    return {
        "name": os.path.basename(target_path),
        "path": request.path,
        "type": file_type,
        "isDirectory": is_dir,
        "size": stats.st_size,
        "created": stats.st_ctime,
        "modified": stats.st_mtime,
        "similar_files": matches,
    }
