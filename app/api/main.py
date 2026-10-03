from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import STATIC_DIR
from app.database import init_db
from app.api.routes import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes the database schema on server startup."""
    init_db()
    yield


app = FastAPI(
    title="Scholarship Intelligence Crawler",
    description="Automated intelligence crawler, evidence verifier, and change detector for Indian scholarships.",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware for development flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def serve_index():
    """Serves the main interactive web dashboard."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "Scholarship Intelligence Crawler API is active. Open /docs for Swagger API documentation."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api.main:app", host="0.0.0.0", port=8000, reload=True)
