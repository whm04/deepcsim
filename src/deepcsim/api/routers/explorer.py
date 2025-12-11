"""Explorer router - endpoints for file exploration and scanning."""

import os
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from deepcsim.core.scanner import scan_directory
from deepcsim.api.schemas import ScanProjectRequest
from deepcsim.api.responses import PrettyJSONResponse

router = APIRouter(tags=["explorer"])

# Setup templates (relative to this router file: ../templates)
current_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(os.path.dirname(current_dir), "templates")
templates = Jinja2Templates(directory=templates_dir)


@router.get("/", response_class=HTMLResponse)
async def explorer(request: Request):
    """Return the file explorer HTML interface."""
    return templates.TemplateResponse("explorer.html", {"request": request})


@router.post("/scan-project", response_class=PrettyJSONResponse)
async def scan_project_endpoint(request: ScanProjectRequest):
    """
    Scan a directory recursively for duplicate/similar Python files.

    Returns a list of file pairs with high similarity scores.
    """
    try:
        result = scan_directory(request.directory, request.threshold)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
