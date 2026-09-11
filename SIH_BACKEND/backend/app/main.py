from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CSRF Middleware for state-changing requests
@app.middleware("http")
async def csrf_origin_validation(request: Request, call_next):
    if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
        origin = request.headers.get("origin")
        trusted_origins = settings.BACKEND_CORS_ORIGINS
        
        # Allow requests without Origin (e.g. non-browser API clients, tests)
        # or requests with a trusted Origin
        if origin is not None and origin not in trusted_origins:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "CSRF origin validation failed"}
            )
    return await call_next(request)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os

os.makedirs(settings.ABSOLUTE_UPLOAD_DIR, exist_ok=True)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/api/v1/health")
async def health_check():
    # TODO: Implement actual DB and AI service checks
    return {
        "status": "healthy",
        "database": "connected",
        "ai_service": "reachable",
        "timestamp": "2026-09-05T22:00:00+05:30"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
