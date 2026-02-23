from fastapi import FastAPI, APIRouter
import os
base_router = APIRouter(
    prefix = "/api/v1",
    tags=["Shymaa_api"]
)

@base_router.get('/Shymaa')
async def Welcom():
    app_name = os.getenv("APP_NAME")
    app_version = os.getenv("APP_VERSION")
    return {
        "app_name" : app_name,
        "app_version" : app_version,
        

    }