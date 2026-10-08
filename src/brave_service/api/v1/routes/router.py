from fastapi import APIRouter

from .admin_router import admin_router
from .auth_router import auth_router

v1_router = APIRouter()
v1_router.include_router(admin_router)
v1_router.include_router(auth_router)
