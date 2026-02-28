from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings, Settings
from controllers import DataController
import aiofiles
from models import ResponseSignal
from controllers.ProjectController import ProjectController
import logging
logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix = "/api/v1/data",
    tags=["api_v1","data"]
)
@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile, app_settings: Settings = Depends(get_settings)):

    data_controller = DataController()
    
    # 1️⃣ validate the file
    is_valid, result_signal = data_controller.validate_upload_file(file=file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"Signal": result_signal, "file ID": None}
        )

    # 2️⃣ prepare paths
    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    file_path, file_id = data_controller.generate_unique_filepath(
        orig_file_name=file.filename,
        project_id=project_id
    )

    # 3️⃣ upload the file
    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error while uploading file {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"Signal": ResponseSignal.FILE_UPLOAD_FAILED.value,
                     "file ID": file_id}
        )

    # 4️⃣ return success
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"Signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                 "file ID": file_id}
    )