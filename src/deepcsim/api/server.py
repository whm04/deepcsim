import os
import uvicorn

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from deepcsim.api.routers import (
    analysis_router,
    explorer_router,
    files_router,
)

# Initialize FastAPI app
app = FastAPI(
    title="DeepCSIM - Code Similarity Analyzer",
    description="Analyze and detect code similarity in Python projects",
    version="0.1.0",
)

# Setup templates
api_dir = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(api_dir, "templates"))

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (CSS, JS)
static_dir = os.path.join(api_dir, "static")
js_dir = os.path.join(static_dir, "js")
css_dir = os.path.join(static_dir, "css")

if os.path.exists(js_dir):
    app.mount("/static/js", StaticFiles(directory=js_dir), name="static_js")

if os.path.exists(css_dir):
    app.mount("/static/css", StaticFiles(directory=css_dir), name="static_css")

# Register routers
app.include_router(analysis_router)
app.include_router(explorer_router)
app.include_router(files_router)


@app.get("/e", response_class=HTMLResponse)
async def home(request: Request):
    """Return the home page HTML."""
    return templates.TemplateResponse("index.html", {"request": request})


def main():
    """Run the development server."""
    uvicorn.run(app, port=8000)


if __name__ == "__main__":
    main()
