from typing import Annotated
from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_active_user, require_user
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[User, Depends(require_user)]
):
    """
    Get current user.
    """
    return current_user
