from fastapi import APIRouter
from app.api.routes import auth, users, inspections, manufacturers, analytics, shared

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(inspections.router, prefix="/inspections", tags=["inspections"])
api_router.include_router(manufacturers.router, prefix="/manufacturers", tags=["manufacturers"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(shared.router, prefix="/shared", tags=["shared"])
