# pyrefly: ignore [missing-import]
from fastapi import Request
# pyrefly: ignore [missing-import]
from fastapi.responses import JSONResponse

class AIAPIException(Exception):
    def __init__(self, category: str, detail: str, status_code: int = 400):
        self.category = category
        self.detail = detail
        self.status_code = status_code

async def ai_api_exception_handler(request: Request, exc: AIAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_category": exc.category,
            "error_detail": exc.detail
        }
    )
