from fastapi import APIRouter

from .routes.admin_router import admin_router

router = APIRouter()
router.include_router(admin_router)
