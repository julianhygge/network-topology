from io import BytesIO
from uuid import UUID

from fastapi import File, Form, APIRouter, HTTPException, status, Request, UploadFile, Depends
from fastapi.responses import JSONResponse
from peewee import DoesNotExist
from starlette.responses import StreamingResponse

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import get_load_profile_service
from app.api.v1.models.requests.load_profile.load_profile_update import LoadProfileBuilderItemsRequest, \
    LoadGenerationEngineResponse, LoadGenerationEngineRequest
from app.api.v1.models.responses.load_profile.load_profile_response import LoadProfileResponse, \
    LoadProfilesListResponse, LoadProfileBuilderItemsResponse, LoadProfileBuilderItemResponse

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


@load_router.post(
    "/houses/{house_id}/load-profile-items",
    response_model=LoadProfileBuilderItemsResponse,
    description="Save load profile builder items for a specific house",
    response_description="The saved load profile builder items"
)
async def save_load_profile_builder_items(
        house_id: UUID,
        items: LoadProfileBuilderItemsRequest,
        service=Depends(get_load_profile_service),
        user_id: str = Depends(permission(Resources.LoadProfiles, Permission.Retrieve)),
):
    try:
        items_dicts = [item.model_dump() for item in items.items]
        updated_items = service.save_load_profile_items(user_id, house_id, items_dicts)

        updated_items_response = [
            LoadProfileBuilderItemResponse(
                id=item.id,
                created_on=item.created_on,
                modified_on=item.modified_on,
                created_by=item.created_by.id,
                profile_id=item.profile_id.id,
                electrical_device_id=item.electrical_device_id.id,
                rating_watts=item.rating_watts,
                quantity=item.quantity,
                hours=item.hours
            )
            for item in updated_items
        ]

        return LoadProfileBuilderItemsResponse(
            message="Items saved successfully",
            items=updated_items_response
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@load_router.get(
    "/houses/{house_id}/load-profile-items",
    response_model=LoadProfileBuilderItemsResponse,
    description="Get builder items for a specific house",
    response_description="The current load profile builder items"
)
async def get_profile_builder_items(
        house_id: UUID,
        service=Depends(get_load_profile_service),
        user_id: str = Depends(permission(Resources.LoadProfiles, Permission.Retrieve)),
):
    try:
        updated_items = service.get_load_profile_builder_items(user_id, house_id)

        updated_items_response = [
            LoadProfileBuilderItemResponse(
                id=item.id,
                created_on=item.created_on,
                modified_on=item.modified_on,
                created_by=item.created_by.id,
                profile_id=item.profile_id.id,
                electrical_device_id=item.electrical_device_id.id,
                rating_watts=item.rating_watts,
                quantity=item.quantity,
                hours=item.hours
            )
            for item in updated_items
        ]

        return LoadProfileBuilderItemsResponse(
            message="Items saved successfully",
            items=updated_items_response
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@load_router.post(
    "/houses/{house_id}/generation-engine",
    response_model=LoadGenerationEngineResponse,
    description="Save load generation engine data for a specific house",
    response_description="The saved load generation engine data"
)
async def save_load_generation_engine(
        house_id: UUID,
        data: LoadGenerationEngineRequest,
        service=Depends(get_load_profile_service),
        user_id: UUID = Depends(permission(Resources.LoadProfiles, Permission.Create)),
):
    try:

        engine = service.save_load_generation_engine(user_id, house_id, data.model_dump())

        return LoadGenerationEngineResponse(
            id=engine.id,
            user_id=engine.user_id.id,
            profile_id=engine.profile_id.id,
            house_id=house_id,
            type=engine.type,
            average_kwh=engine.average_kwh,
            average_monthly_bill=engine.average_monthly_bill,
            max_demand_kw=engine.max_demand_kw,
            created_on=engine.created_on,
            modified_on=engine.modified_on
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@load_router.get(
    "/houses/{house_id}/generation-engine",
    response_model=LoadGenerationEngineResponse,
    description="Get load generation engine data for a specific house",
    response_description="The load generation engine data"
)
async def get_load_generation_engine(
        house_id: UUID,
        service=Depends(get_load_profile_service),
        user_id: UUID = Depends(permission(Resources.LoadProfiles, Permission.Retrieve)),
):
    try:

        engine = service.get_load_generation_engine(user_id, house_id)
        if engine is None:
            raise HTTPException(status_code=404, detail="Load generation engine data not found")

        return LoadGenerationEngineResponse(
            id=engine.id,
            user_id=engine.user_id.id,
            profile_id=engine.profile_id.id,
            house_id=house_id,
            type=engine.type,
            average_kwh=engine.average_kwh,
            average_monthly_bill=engine.average_monthly_bill,
            max_demand_kw=engine.max_demand_kw,
            created_on=engine.created_on,
            modified_on=engine.modified_on
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
