"""API endpoints for managing Load Profile file operations."""

from io import BytesIO
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import JSONResponse
from peewee import DoesNotExist
from starlette.responses import StreamingResponse

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import (
    get_load_profile_file_service,
)
from app.domain.services.solar.load_profile_file_service import (
    LoadProfileFileService,
)

files_router = APIRouter(tags=["Load Profile"])


@files_router.post("/upload/", status_code=status.HTTP_202_ACCEPTED)
# pylint: disable=too-many-arguments
async def upload_load_profile(
    request: Request,
    file: UploadFile = File(...),
    interval_15_minutes: bool = Form(...),
    house_id: UUID = Form(...),
    profile_name: str = Form(None),
    user_id: str = Depends(
        permission(Resources.LOAD_PROFILES, Permission.CREATE)
    ),
    load_profile_file_service: LoadProfileFileService = Depends(
        get_load_profile_file_service
    ),
):
    """
    Upload a load profile file for a specific house.

    Args:
        request: The incoming request object.
        file: The uploaded file.
        interval_15_minutes: Flag indicating if the data is in
        15-min intervals.
        house_id: The ID of the house the profile belongs to.
        profile_name: Optional name for the profile (defaults to filename).
        user_id: The ID of the user uploading the file (from permission).
        load_profile_file_service: Injected load profile file service instance.

    Returns:
        JSONResponse indicating success or failure, with links.
    """
    if not profile_name:
        profile_name = file.filename

    try:
        data = await load_profile_file_service.upload_profile_file(
            user_id, profile_name, file, interval_15_minutes, house_id
        )
        self = str(request.url.path)
        download = self.replace("/upload/", "/download/")
        download = f"{download}file?profile_id={data['profile_id']}"
        delete = self.replace("/upload/", "/")
        delete = f"{delete}{data['profile_id']}/"
        content = {
            "house_id": str(data["house_id"]),
            "message": "File uploaded successfully",
            "profile_id": data["profile_id"],
            "file_name": data["file_name"],
            "user": data["user_id"],
            "links": {"download": download, "delete": delete, "self": self},
        }
        return JSONResponse(
            content=content, status_code=status.HTTP_202_ACCEPTED
        )
    except Exception as exc:  # pylint: disable=broad-exception-caught
        return JSONResponse(
            content={"message": str(exc)},
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@files_router.get("/download/file", status_code=status.HTTP_202_ACCEPTED)
async def download_load_profile_file(
    profile_id: int,
    load_profile_file_service: LoadProfileFileService = Depends(
        get_load_profile_file_service
    ),
    _: str = Depends(permission(Resources.LOAD_PROFILES, Permission.RETRIEVE)),
):
    """
    Download the file content of a specific load profile.

    Args:
        profile_id: The ID of the load profile file to download.
        load_profile_file_service: Injected load profile file service instance.
        _: Dependency to check retrieve permission.

    Returns:
        StreamingResponse containing the file content.

    Raises:
        HTTPException: 404 if the file is not found.
    """
    try:
        file_record = load_profile_file_service.get_load_profile_file_content(
            profile_id
        )
        return StreamingResponse(
            BytesIO(file_record.content),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment;filename={file_record.filename}"
            },
        )
    except DoesNotExist as exc:
        raise HTTPException(status_code=404, detail="File not found") from exc
