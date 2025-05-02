from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from app.api.authorization.authorization import permission
from app.api.authorization.enums import Resources, Permission
from app.api.v1.dependencies.container_instance import get_user_service
from app.api.v1.models.requests.auth.auth_request import UserRequestModel
from app.api.v1.models.responses.auth.auth_response import UserResponseModel, UserListResponse, UserLinkResponseModel
from app.domain.interfaces.i_service import IService
from starlette.requests import Request
from app.exceptions.hygge_exceptions import NotFoundException

user_router = APIRouter(tags=["Users"])


@user_router.post(path="/", response_model=UserResponseModel)
async def create_user(user_data: UserRequestModel,
                      user_id: str = Depends(permission(Resources.Users, Permission.Create)),
                      service: IService = Depends(get_user_service)):
    body = service.create(user_id, **user_data.model_dump())
    return UserResponseModel(**body)


@user_router.get(path="/", response_model=UserListResponse)
async def get_users(request: Request,
                    service: IService = Depends(get_user_service),
                    _: str = Depends(permission(Resources.Users, Permission.Retrieve)),
                    ):
    try:
        data_list = service.list_all()
        response = UserListResponse(items=[
            UserLinkResponseModel(
                **item,
                links={"self": f"{request.url.path}{str(item['id'])}"}
            ) for item in data_list
        ])
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_router.put(path="/{user_id}", response_model=UserResponseModel)
async def update(request: Request,
                 user_data: UserRequestModel,
                 user_id: UUID,
                 logged_user_id: str = Depends(permission(Resources.Users, Permission.Update)),
                 service: IService = Depends(get_user_service)):
    try:
        updated_data = service.update(logged_user_id, user_id,
                                      **user_data.model_dump(exclude_unset=True))
        if updated_data is None:
            raise NotFoundException()
        updated_data['links'] = {"self": f"{request.url.path}{user_id}/"}
        return UserResponseModel(**updated_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_router.delete(path="/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(user_id: UUID,
                 _=Depends(permission(Resources.Users, Permission.Delete)),
                 service: IService = Depends(get_user_service)):
    delete_result = service.delete(user_id)
    if not delete_result:
        raise NotFoundException()
