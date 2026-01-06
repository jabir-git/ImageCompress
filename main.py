"""Image Compressor & Converter - FastAPI Application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn

from routers.images import router as images_router

# Application Configuration
APP_TITLE = "Image Compressor & Converter"
STATIC_DIR = "static"
TEMPLATES_DIR = "templates"
API_PREFIX = "/api"

# Create FastAPI app
app = FastAPI(title=APP_TITLE)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount(f"/{STATIC_DIR}", StaticFiles(directory=STATIC_DIR), name=STATIC_DIR)
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Include routers
app.include_router(images_router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with custom 404 page."""
    if exc.status_code == 404:
        return templates.TemplateResponse(
            "404.html", {"request": request}, status_code=404
        )
    raise exc


@app.get("/")
async def home(request: Request):
    """Render home page."""
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0")
