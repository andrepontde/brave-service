from fastapi import FastAPI

from brave_service.api.v1.router import router as v1_router

app = FastAPI()
app.include_router(v1_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"Hello": "World"}