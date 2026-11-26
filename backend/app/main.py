import logging
import os
from uuid import uuid4

from app.routers import (
    alerts,
    analysis,
    clusters,
    datasets,
    graph,
    investigations,
    models,
    stats,
)
from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

docs_enabled = os.getenv("NIRIKSHAK_ENABLE_DOCS") == "1"
origins = os.getenv(
    "NIRIKSHAK_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
)
allow_origins = [origin.strip() for origin in origins.split(",") if origin.strip()]
if "*" in allow_origins:
    raise ValueError("Configure explicit CORS origins")

app = FastAPI(
    docs_url="/docs" if docs_enabled else None,
    redoc_url="/redoc" if docs_enabled else None,
    openapi_url="/openapi.json" if docs_enabled else None,
    title="NIRIKSHAK AI - Bitcoin Transaction Intelligence API",
    description="Offline AI-powered Bitcoin transaction investigation & traffic analysis platform backend (SIH26146).",
    version="0.1.0",
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(datasets.router, prefix="/api/datasets", tags=["Datasets"])
app.include_router(stats.router, prefix="/api", tags=["Stats"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(graph.router, prefix="/api/graph", tags=["Graph"])
app.include_router(
    investigations.router, prefix="/api/investigations", tags=["Investigations"]
)
app.include_router(clusters.router, prefix="/api/clusters", tags=["Clusters"])
app.include_router(models.router, prefix="/api/model", tags=["Model Analytics"])


@app.get("/")
def read_root():
    return {
        "service": "NIRIKSHAK AI Backend",
        "problem_statement": "SIH26146 - AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic",
        "status": "active",
        "version": "0.1.0",
    }


@app.get("/health")
@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "nirikshak-backend", "version": "0.1.0"}


def server_error(request: Request, exc: Exception) -> JSONResponse:
    """Log failure details with a correlation ID and return a generic response."""
    request_id = uuid4().hex
    logging.getLogger(__name__).error(
        "Server error for %s request, ID %s", request.method, request_id, exc_info=exc
    )
    return JSONResponse(
        status_code=500,
        headers={"X-Request-ID": request_id},
        content={"detail": "Internal server error", "request_id": request_id},
    )


@app.exception_handler(HTTPException)
async def handle_http_error(request: Request, exc: HTTPException):
    if exc.status_code >= 500:
        return server_error(request, exc)
    return await http_exception_handler(request, exc)


@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    return server_error(request, exc)
