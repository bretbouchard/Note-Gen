"""Main FastAPI application."""
from fastapi import FastAPI
from src.note_gen.routers.router import router  # Use relative import

app = FastAPI(
    title="Note Generator API",
    description="API for generating musical patterns and sequences",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
