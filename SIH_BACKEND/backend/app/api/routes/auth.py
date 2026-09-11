from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db
from app.core.security import create_access_token
from app.services.auth_service import authenticate
from app.schemas.auth import Token

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_access_token(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    access_token = create_access_token(subject=user.email)
    
    user_dict = {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "role": user.role
    }
    
    response = JSONResponse(content={
        "access_token": "cookie",
        "token_type": "cookie",
        "expires_in": 60 * 24 * 8, # placeholder, though usually handled by client
        "user": user_dict
    })
    
    # Set HttpOnly cookie for auth
    import os
    import secrets
    is_prod = os.getenv("ENVIRONMENT") == "production"
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=is_prod,
        path="/"
    )
    
    # Set non-HttpOnly cookie for CSRF token
    csrf_token = secrets.token_urlsafe(32)
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        samesite="lax",
        secure=is_prod,
        path="/"
    )
    
    return response

@router.post("/logout")
async def logout(response: Response):
    """
    Logout the user by clearing the HttpOnly cookie and CSRF cookie.
    """
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="csrf_token", path="/")
    return {"message": "Logged out successfully"}
