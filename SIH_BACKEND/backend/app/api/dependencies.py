from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status, Request
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import get_user_by_email

def get_token_from_cookie(request: Request) -> Optional[str]:
    return request.cookies.get("access_token")

async def get_current_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    token = get_token_from_cookie(request)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    
    if not token:
        raise credentials_exception
        
    # Validate CSRF for state-changing requests
    if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
        csrf_header = request.headers.get("x-csrf-token")
        csrf_cookie = request.cookies.get("csrf_token")
        if not csrf_header or not csrf_cookie or csrf_header != csrf_cookie:
            raise HTTPException(status_code=403, detail="CSRF validation failed")
        
        # Untrusted Origin validation
        origin = request.headers.get("origin")
        if origin and origin not in settings.BACKEND_CORS_ORIGINS:
            raise HTTPException(status_code=403, detail="Untrusted Origin")
        
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

def require_role(allowed_roles: list[str]):
    async def role_dependency(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_dependency

require_user = require_role(["USER", "OFFICER", "ADMIN"])
require_officer = require_role(["OFFICER", "ADMIN"])
require_admin = require_role(["ADMIN"])
