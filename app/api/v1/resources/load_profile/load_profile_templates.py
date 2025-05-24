"""API endpoints for managing Load Profile template operations."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import (
    get_load_profile_template_service,
    get_predefined_template_service,
)
from app.api.v1.models.requests.load_profile.load_profile_create import (
    GenerateProfileFromTemplateRequest,
)
from app.api.v1.models.requests.load_profile.load_profile_update import (
    LoadPredefinedTemplateRequest,
)
from app.api.v1.models.responses.load_profile.load_profile_response import (
    LoadPredefinedMasterTemplateResponse,
    LoadPredefinedTemplateListResponse,
    LoadPredefinedTemplateResponse,
)
from app.domain.interfaces.i_service import IService
from app.domain.services.solar.load_profile_template_service import (
    LoadProfileTemplateService,
)

templates_router = APIRouter(tags=["Load Profile"])


@templates_router.post(
    "/houses/{house_id}/load-predefined-template",
    response_model=LoadPredefinedTemplateResponse,
    description="Create or update a load template for a specific house",
    response_description="The created or updated load predefined template",
)
async def create_or_update_load_predefined_template(
    request: Request,
    house_id: UUID,
    template_data: LoadPredefinedTemplateRequest,
    load_profile_template_service: LoadProfileTemplateService = Depends(
        get_load_profile_template_service
    ),
    user_id: UUID = Depends(
        permission(Resources.LOAD_PROFILES, Permission.CREATE)
    ),
):
    """
    Create or update a load predefined template for a specific house.

    Args:
        request: The incoming request object.
        house_id: The ID of the house.
        template_data: The predefined template data.
        load_profile_template_service: Injected load profile template service instance.
        user_id: The ID of the user making the request (from permission).

    Returns:
        The created or updated load predefined template with links.

    Raises:
        HTTPException: 500 if an error occurs during the operation.
    """
    try:
        template = load_profile_template_service.create_or_update_load_predefined_template(
            user_id, house_id, template_data.template_id
        )
        index = request.url.path.find("/load/")
        if index != -1:
            new_url_path = request.url.path[: index + len("/load/")]
        else:
            new_url_path = request.url.path
        delete = f"{new_url_path}{template.profile_id.id}/"

        return LoadPredefinedTemplateResponse(
            id=template.id,
            profile_id=template.profile_id.id,
            template_id=template.template_id.id,
            name=template.template_id.name,
            power_kw=template.template_id.power_kw,
            profile_source=template.profile_id.source,
            links={"delete": delete},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@templates_router.get(
    "/houses/{house_id}/load-predefined-template",
    response_model=LoadPredefinedTemplateResponse,
    description="Get the load predefined template for a specific house",
    response_description="The load predefined template",
)
async def get_load_predefined_template(
    request: Request,
    house_id: UUID,
    load_profile_template_service: LoadProfileTemplateService = Depends(
        get_load_profile_template_service
    ),
    user_id: UUID = Depends(
        permission(Resources.LOAD_PROFILES, Permission.RETRIEVE)
    ),
):
    """
    Get the load predefined template for a specific house.

    Args:
        request: The incoming request object.
        house_id: The ID of the house.
        load_profile_template_service: Injected load profile template service instance.
        user_id: The ID of the user making the request (from permission).

    Returns:
        The load predefined template with links.

    Raises:
        HTTPException: 404 if the template is
        not found, 500 for unexpected errors.
    """
    try:
        template = load_profile_template_service.get_load_predefined_template(
            user_id, house_id
        )
        if template is None:
            raise HTTPException(
                status_code=404, detail="Load predefined template not found"
            )
        index = request.url.path.find("/load/")
        if index != -1:
            new_url_path = request.url.path[: index + len("/load/")]
        else:
            new_url_path = request.url.path

        delete = f"{new_url_path}{template.profile_id.id}/"
        return LoadPredefinedTemplateResponse(
            id=template.id,
            profile_id=template.profile_id.id,
            template_id=template.template_id.id,
            name=template.template_id.name,
            power_kw=template.template_id.power_kw,
            profile_source=template.profile_id.source,
            links={"delete": delete},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@templates_router.get(
    "/load_templates", response_model=LoadPredefinedTemplateListResponse
)
async def get_load_templates(
    service: IService = Depends(get_predefined_template_service),
    _: str = Depends(permission(Resources.ELECTRICALS, Permission.RETRIEVE)),
):
    """
    Get a list of all predefined load templates.

    Args:
        service: Injected predefined template service instance.
        _: Dependency to check retrieve permission.

    Returns:
        A list of predefined load templates.

    Raises:
        HTTPException: 400 if an error occurs during retrieval.
    """
    try:
        body = service.list_all()
        response = LoadPredefinedTemplateListResponse(
            items=[
                LoadPredefinedMasterTemplateResponse(**item) for item in body
            ]
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@templates_router.post(
    "/template/generate",
    status_code=status.HTTP_201_CREATED,
    response_description="Load profile generated from template successfully",
)
async def generate_load_profile_from_template(
    request: Request,
    generate_request: GenerateProfileFromTemplateRequest,
    load_profile_template_service: LoadProfileTemplateService = Depends(
        get_load_profile_template_service
    ),
    _: UUID = Depends(permission(Resources.LOAD_PROFILES, Permission.CREATE)),
):
    """
    Generate a 15-minute interval load profile from a predefined template
    and household characteristics.

    Args:
        template_id: id of the predefined template.
        load_profile_template_service: Injected load profile template service instance.
        user_id: The ID of the user making the request (from permission).

    Returns:
        JSONResponse indicating success or failure.

    Raises:
        HTTPException: 400 for bad requests, 500 for server errors.
    """
    try:
        generated_profile_info = (
            await load_profile_template_service.generate_profile_from_template(
                generate_request.template_id,
                generate_request.people_profiles,
            )
        )

        profile_id = generated_profile_info.get("profile_id")

        links = {}
        if profile_id:
            base_url = str(request.url_for("list_load_profiles")).split("?")[
                0
            ]  # Get base path for profiles
            links["profile_details"] = f"{base_url}{profile_id}/details"

        return JSONResponse(
            content={
                "message": "Load profile generated successfully from template",
                "template_id": generate_request.template_id,
                "links": links,
            },
            status_code=status.HTTP_201_CREATED,
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve)
        ) from ve
    except Exception as e:
        # Log the exception e for debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating the profile",
        ) from e
