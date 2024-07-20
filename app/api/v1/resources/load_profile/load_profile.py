from fastapi import File, Form, APIRouter, HTTPException, status, Request, UploadFile, Depends
from fastapi.responses import JSONResponse
from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import get_load_profile_service
from app.api.v1.models.requests.load_profile.load_profile_create import LoadProfileCreateRequest
from app.api.v1.models.responses.load_profile.load_profile_response import LoadProfileResponse, LoadProfilesListResponse
from app.exceptions.hygge_exceptions import NotFoundException

load_router = APIRouter(tags=["Load Profile"])


@load_router.post("/", response_model=LoadProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_load_profile(request: Request, load_profile_data: LoadProfileCreateRequest,
                              user_id: str = Depends(permission(Resources.LoadProfiles,
                                                                Permission.Create)),
                              load_profile_service=Depends(get_load_profile_service)):
    try:
        response = load_profile_service.add_profile(user_id, **load_profile_data.model_dump())
        load_profile_id = response["load_profile_id"]
        self_url = f"{request.url.path}{load_profile_id}"
        response['links'] = {"self": self_url}
        response['status_message'] = "Created"
        return LoadProfileResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@load_router.get("/{load_profile_id}/", response_model=LoadProfileResponse)
async def get_load_profile(request: Request, load_profile_id: int,
                           _=Depends(permission(Resources.LoadProfiles, Permission.Retrieve)),
                           service=Depends(get_load_profile_service)):
    data = service.read(load_profile_id)
    if data is None:
        raise NotFoundException(message="Profile not found")
    data['links'] = {"self": f"{request.url.path}"}
    return LoadProfileResponse(**data)


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
                             user_id: str = Depends(permission(Resources.LoadProfiles,
                                                               Permission.Retrieve)),
                             load_profile_service=Depends(get_load_profile_service)):
    try:
        profiles = load_profile_service.list_profiles(user_id)
        items = []
        for profile in profiles:
            self_link = f"{request.url.path}{profile['load_profile_id']}"
            profile_data = {**profile, "links": {"self": self_link}}
            profile_response = LoadProfileResponse(**profile_data)
            items.append(profile_response)
        response = LoadProfilesListResponse(items=items)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@load_router.post("/upload/", status_code=status.HTTP_202_ACCEPTED)
async def upload_load_profile(profile_name: str = Form(...), file: UploadFile = File(...),
                              user_id: str = Depends(permission(Resources.LoadProfiles,
                                                                Permission.Create)),
                              load_profile_service=Depends(get_load_profile_service)):
    try:
        await load_profile_service.upload_profile_service_file(user_id, profile_name, file)
        return JSONResponse(content={"message": "File uploaded successfully", "filename": file.filename},
                            status_code=status.HTTP_202_ACCEPTED)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
