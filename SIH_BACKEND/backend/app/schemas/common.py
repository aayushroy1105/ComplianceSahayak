from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field

T = TypeVar("T")

class Pagination(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    pagination: Pagination

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None

class ErrorResponse(BaseModel):
    error: ErrorDetail
