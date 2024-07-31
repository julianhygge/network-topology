from io import BytesIO
from typing import List
from uuid import UUID

from fastapi import File, Form, APIRouter, HTTPException, status, Request, UploadFile, Depends
from fastapi.responses import JSONResponse
from peewee import DoesNotExist
from starlette.responses import StreamingResponse
from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import get_load_profile_service
from app.api.v1.models.responses.load_profile.load_profile_response import LoadProfileResponse, LoadProfilesListResponse

load_router = APIRouter(tags=["Load Profile"])


@load_router.delete("/{load_profile_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_load_profile(load_profile_id: int,
                              _=Depends(permission(Resources.LoadProfiles, Permission.Delete)),
                              load_profile_service=Depends(get_load_profile_service)):
    try:
        result = load_profile_service.delete_profile(load_profile_id)
        if not result:
            raise HTTPException(status_code=404, detail="Load profile not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@load_router.get("/", response_model=LoadProfilesListResponse, status_code=status.HTTP_200_OK)
async def list_load_profiles(request: Request,
                             house_id: UUID,
                             user_id: str = Depends(permission(Resources.LoadProfiles,
                                                               Permission.Retrieve)),
                             load_profile_service=Depends(get_load_profile_service)):
    try:
        return await _get_load_profiles(load_profile_service, user_id, house_id, request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def _get_load_profiles(load_profile_service, user_id, house_id, request):
    profiles = load_profile_service.list_profiles(user_id, house_id)
    items = []
    for profile in profiles:
        self = str(request.url.path)
        download = self.replace("/upload/", "/download/")
        download = f"{download}file?profile_id={profile['profile_id']}"
        delete = self.replace("/upload/", "/")
        delete = f"{delete}{profile['profile_id']}/"
        profile_data = {**profile, "links": {
            "self": self,
            "delete": delete,
            "download": download
        }}
        profile_response = LoadProfileResponse(**profile_data)
        items.append(profile_response)
    response = LoadProfilesListResponse(items=items)
    return response


@load_router.post("/upload/", status_code=status.HTTP_202_ACCEPTED)
async def upload_load_profile(
        request: Request,
        file: UploadFile = File(...),
        interval_15_minutes: bool = Form(...),
        house_id: UUID = Form(...),
        profile_name: str = Form(None),
        user_id: str = Depends(permission(Resources.LoadProfiles, Permission.Create)),
        load_profile_service=Depends(get_load_profile_service)
):
    if not profile_name:
        profile_name = file.filename

    try:
        data = await load_profile_service.upload_profile_service_file(
            user_id,
            profile_name,
            file,
            interval_15_minutes,
            house_id
        )
        self = str(request.url.path)
        download = self.replace("/upload/", "/download/")
        download = f"{download}file?profile_id={data['profile_id']}"
        delete = self.replace("/upload/", "/")
        delete = f"{delete}{data['profile_id']}/"
        content = {
            "house_id": str(data['house_id']),
            "message": "File uploaded successfully",
            "profile_id": data['profile_id'],
            "file_name": data['file_name'],
            "user": data['user'],
            "links": {
                "download": download,
                "delete": delete,
                "self": self
            }
        }
        return JSONResponse(content=content, status_code=status.HTTP_202_ACCEPTED)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


@load_router.get("/download/file", status_code=status.HTTP_202_ACCEPTED)
async def download_load_profile_file(
        profile_id: int,
        service=Depends(get_load_profile_service),
        _: str = Depends(permission(Resources.LoadProfiles, Permission.Retrieve))):
    try:
        file_record = service.get_load_profile_file(profile_id)
        return StreamingResponse(BytesIO(file_record.content), media_type="application/octet-stream",
                                 headers={"Content-Disposition": f"attachment;filename={file_record.filename}"})
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="File not found")


@load_router.post("/houses/{house_id}/load-profile-items")
async def save_load_profile_builder_items(
        house_id: UUID,
        items: List[dict],
        service=Depends(get_load_profile_service),
        _: str = Depends(permission(Resources.LoadProfiles, Permission.Retrieve))):
    try:
        updated_items = service.save_load_profile_items(house_id, items)
        return {"message": "Items saved successfully", "items": updated_items}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
