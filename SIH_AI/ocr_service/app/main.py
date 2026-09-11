from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.routes import router
from app.config import settings
from app.engine import ocr_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the OCR model lazily but persistently at startup
    ocr_engine.initialize()
    yield
    # Cleanup if necessary

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION, lifespan=lifespan)

app.include_router(router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc.errors())}
    )
