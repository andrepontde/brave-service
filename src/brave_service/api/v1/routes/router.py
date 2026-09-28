from fastapi import APIRouter

from .admin_router import admin_router

v1_router = APIRouter()
v1_router.include_router(admin_router)
