import os

import uvicorn
from fastapi import FastAPI

from brave_service.api.v1.routes import v1_router

app = FastAPI()
app.include_router(v1_router, prefix="/api/v1")

def main() -> None:
	uvicorn.run(
		"brave_service.main:app",
		host=os.getenv("HOST", "127.0.0.1"),
		port=int(os.getenv("PORT", "8000")),
	)