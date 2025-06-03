"""API endpoints for managing substations and their topology."""

import io
import os
import shutil
from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import UUID4

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import (
    get_data_preparation_service,
    get_net_topology_service,
    get_substation_service, get_net_topology_export_import_service,
)
from app.api.v1.models.requests.substation import (
    SubstationRequestModel,
    SubstationsRequestModel,
    SubstationTopologyRequestModel,
)
from app.api.v1.models.requests.transformer_requests import HouseResponseModel
from app.api.v1.models.responses.house import HouseResponseModelList
from app.api.v1.models.responses.substation import (
    SubstationResponseModel,
    SubstationResponseModelList,
    SubstationTopology,
)
from app.domain.interfaces.i_service import IService
from app.domain.interfaces.net_topology.i_net_topology_service import (
    INetTopologyService,
)
from app.domain.interfaces.net_topology.i_substation_service import (
    ISubstationService,
)
from app.domain.interfaces.simulator_engine.i_data_preparation_service import (
    IDataPreparationService,
)
from app.domain.services.simulator_engine.net_topology_export_import_service import NetTopologyExportImportService
from app.exceptions.hygge_exceptions import NotFoundException
from app.utils.logger import logger

substation_router = APIRouter(tags=["Substations"])

SubstationsRetrievePermissionDep = Depends(
    permission(Resources.SUBSTATIONS, Permission.RETRIEVE)
)
GetNetTopologyServiceDep = Depends(get_net_topology_service)
SubstationsUpdatePermissionDep = Depends(
    permission(Resources.SUBSTATIONS, Permission.UPDATE)
)
SubstationsCreatePermissionDep = Depends(
    permission(Resources.SUBSTATIONS, Permission.CREATE)
)
GetSubstationServiceDep = Depends(get_substation_service)
GetDataPreparationServiceDep = Depends(get_data_preparation_service)
SubstationsDeletePermissionDep = Depends(
    permission(Resources.SUBSTATIONS, Permission.DELETE)
)
GetNetTopologyExportImportService = Depends(get_net_topology_export_import_service)


@substation_router.get("/{substation_id}", response_model=SubstationTopology)
async def get_substation_topology(
        substation_id: UUID,
        _: str = SubstationsRetrievePermissionDep,
        service: INetTopologyService = GetNetTopologyServiceDep,
) -> SubstationTopology:
    """
    Retrieve the topology structure for a specific substation.

    Requires retrieve permission on the Substations resource.

    Args:
        substation_id: The ID of the substation.
        _: Placeholder for permission dependency.
        service: Injected network topology service instance.

    Returns:
        The topology structure starting from the substation.

    Raises:
        HTTPException: If the substation is not found (404).
    """
    topology = service.get_topology_by_substation_id(str(substation_id))
    if not topology:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Substation not found",
        )
    return SubstationTopology(**topology)


@substation_router.put("/{substation_id}", response_model=SubstationTopology)
async def update_substation_topology(
        substation_id: UUID4,
        topology_data: SubstationTopologyRequestModel,
        user_id: str = SubstationsUpdatePermissionDep,
        service: INetTopologyService = GetNetTopologyServiceDep,
) -> SubstationTopology:
    """
    Update the topology structure for a specific substation.

    Requires update permission on the Substations resource.

    Args:
        substation_id: The ID of the substation to update.
        topology_data: The new topology structure data.
        user_id: ID of the user performing the action (from permission).
        service: Injected network topology service instance.

    Returns:
        The updated topology structure.

    Raises:
        HTTPException: If the substation is not found after update (404).
        (Indicates potential issue if update succeeded but fetch failed)
    """
    service.update_topology(user_id, substation_id, topology_data.model_dump())
    # Fetch again to return the updated topology
    topology = service.get_topology_by_substation_id(str(substation_id))
    if not topology:
        logger.error(
            "Failed to fetch topology after update for %s", substation_id
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Substation not found after update attempt.",
        )
    return SubstationTopology(**topology)


@substation_router.post("/", response_model=SubstationResponseModel)
async def create(
        data: SubstationRequestModel,
        user_id: UUID = SubstationsCreatePermissionDep,
        service: IService = GetSubstationServiceDep,
) -> SubstationResponseModel:
    """
    Create a new substation.

    Requires create permission on the Substations resource.

    Args:
        data: Request body containing substation details.
        user_id: ID of the user performing the action (from permission).
        service: Injected substation service instance.

    Returns:
        The created substation details.
    """
    body = service.create(str(user_id), **data.model_dump())
    return SubstationResponseModel(**body)


@substation_router.post(
    "/generate", response_model=SubstationResponseModelList
)
async def generate_substations(
        data: SubstationsRequestModel,
        user_id: UUID = SubstationsCreatePermissionDep,
        service: ISubstationService = GetSubstationServiceDep,
) -> SubstationResponseModelList:
    """
    Generate multiple substations within a locality.

    Requires create permission on the Substations resource.

    Args:
        data: Request body specifying locality and number of substations.
        user_id: ID of the user performing the action (from permission).
        service: Injected substation service instance.

    Returns:
        A list of the newly created substations.

    Raises:
        HTTPException: If an error occurs during bulk creation.
    """
    try:
        data_list = service.create_bulk(user_id, **data.model_dump())
        response = SubstationResponseModelList(
            items=[SubstationResponseModel(**item) for item in data_list]
        )
        return response
    except Exception as e:
        logger.exception("Error generating substations: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e


@substation_router.get("", response_model=SubstationResponseModelList)
async def get(
        _: str = SubstationsRetrievePermissionDep,
        service: IService = GetSubstationServiceDep,
) -> SubstationResponseModelList:
    """
    Retrieve a list of all substations.

    Requires retrieve permission on the Substations resource.

    Args:
        _: Placeholder for permission dependency.
        service: Injected substation service instance.

    Returns:
        A list of all substations, sorted by creation date.

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        data_list = service.list_all()
        # Ensure sorting happens correctly, assuming 'created_on' exists
        data_list.sort(key=lambda x: x.get("created_on", datetime.min))
        response = SubstationResponseModelList(
            items=[SubstationResponseModel(**item) for item in data_list]
        )
        return response
    except Exception as e:
        logger.exception("Error retrieving substations: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e


@substation_router.get(
    "/{substation_id}/houses", response_model=HouseResponseModelList
)
async def get_houses_by_substation_id(
        substation_id: UUID,
        _: str = SubstationsRetrievePermissionDep,
        service: INetTopologyService = GetNetTopologyServiceDep,
) -> HouseResponseModelList:
    """
    Retrieve the houses for a given substation ID.

    Requires retrieve permission on the Substations resource.

    Args:
        substation_id: The ID of the substation.
        _: Placeholder for permission dependency.
        service: Injected network topology service instance.

    Returns:
        A list of houses associated with the substation.

    Raises:
        HTTPException: If the substation is not found (404).
    """
    try:
        houses_data = service.get_houses_by_substation_id(substation_id)
        items = [HouseResponseModel.model_validate(h) for h in houses_data]
        return HouseResponseModelList(items=items)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e


@substation_router.get(
    "/{substation_id}/houses_profiles", response_model=HouseResponseModelList
)
async def get_houses_profiles_by_substation_id(
        substation_id: UUID,
        _: str = SubstationsRetrievePermissionDep,
        service: IDataPreparationService = GetDataPreparationServiceDep,
) -> HouseResponseModelList:
    """
    Retrieve the house profiles for a given substation ID.

    Requires retrieve permission on the Substations resource.

    Args:
        substation_id: The ID of the substation.
        _: Placeholder for permission dependency.
        service: Injected data preparation service instance.

    Returns:
        A list of house profiles. (Currently uses HouseResponseModelList)

    Raises:
        HTTPException: If the substation is not found (404).
    """
    try:
        house_profiles = service.get_houses_profile_by_substation_id(
            substation_id
        )
        items = [
            HouseResponseModel.model_validate(hp) for hp in house_profiles
        ]
        return HouseResponseModelList(items=items)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e


@substation_router.delete(
    path="/{substation_id}/delete", status_code=status.HTTP_204_NO_CONTENT
)
async def delete(
        substation_id: UUID,
        service: IService = GetSubstationServiceDep,
        _: str = SubstationsDeletePermissionDep,
) -> None:
    """
    Delete a substation.

    Requires delete permission on the Substations resource.

    Args:
        substation_id: The ID of the substation to delete.
        service: Injected substation service instance.
        _: Placeholder for permission dependency.

    Raises:
        HTTPException: If an error occurs during deletion.
    """
    try:
        service.delete(substation_id)
    except Exception as e:
        logger.exception("Error deleting substation %s: %s", substation_id, e)
        raise HTTPException(status_code=400, detail=str(e)) from e


@substation_router.post(
    "/{substation_id}/profiles/csvs",
    status_code=status.HTTP_201_CREATED,
    response_model=List[str],
)
async def create_house_profiles_csv_files(
        substation_id: UUID,
        _: str = SubstationsCreatePermissionDep,
        service: IDataPreparationService = GetDataPreparationServiceDep,
) -> List[str]:
    """
    Generate CSV files for all house profiles under a specific substation.
    The files will be saved in a directory named 'house_profiles_csv'.
    Returns a list of paths to the generated CSV files.
    """
    try:
        # Define a temporary directory for CSVs for this request
        # This helps in managing files if multiple requests occur
        # and for cleanup.
        output_dir = f"temp_house_profiles_csv_{substation_id}"
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir, exist_ok=True)

        file_paths = service.create_house_profile_csvs_by_substation_id(
            substation_id, output_directory=output_dir
        )
        # The service now saves files to the specified output_dir.
        # We might want to return relative paths or just a success message.
        # For now, returning absolute paths as generated by the service.

        return file_paths
    except NotFoundException as e:
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except Exception as e:
        logger.exception(
            "Error generating CSV profiles for substation %s: %s",
            substation_id,
            e,
        )
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate CSV profiles.",
        ) from e


@substation_router.get("/{substation_id}/profiles/zip")
async def get_house_profiles_zip_file(
        substation_id: UUID,
        _: str = SubstationsRetrievePermissionDep,
        service: IDataPreparationService = GetDataPreparationServiceDep,
):
    """
    Retrieve a ZIP file containing CSVs of all house profiles for a substation.
    The CSV files are generated on-the-fly if not already present from a
    previous call to the POST endpoint.
    """
    try:
        # The service method get_house_profile_csvs_zip_by_substation_id
        # internally calls create_house_profile_csvs_by_substation_id,
        # which saves files to a default or specified directory.
        # We'll use a temporary directory for this operation to ensure
        # files are cleaned up.
        temp_output_dir = f"temp_zip_profiles_csv_{substation_id}"
        if os.path.exists(temp_output_dir):  # Clean up if exists
            shutil.rmtree(temp_output_dir)
        os.makedirs(temp_output_dir, exist_ok=True)

        zip_bytes = service.get_house_profile_csvs_zip_by_substation_id(
            substation_id, output_directory=temp_output_dir
        )

        # Clean up the temporary directory after generating the zip
        if os.path.exists(temp_output_dir):
            shutil.rmtree(temp_output_dir)

        return StreamingResponse(
            io.BytesIO(zip_bytes),
            media_type="application/zip",
            headers={
                "Content-Disposition": "attachment;"
                                       "filename=house_profiles_{substation_id}.zip"
            },
        )
    except NotFoundException as e:
        if os.path.exists(temp_output_dir):
            shutil.rmtree(temp_output_dir)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except Exception as e:
        logger.exception(
            "Error generating ZIP file for substation %s: %s", substation_id, e
        )
        if os.path.exists(temp_output_dir):
            shutil.rmtree(temp_output_dir)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate ZIP file.",
        ) from e


@substation_router.get("/{substation_id}/export/json")
async def get_network_topology_export_file(
        substation_id: UUID,
        _: str = SubstationsRetrievePermissionDep,
        service: NetTopologyExportImportService = GetNetTopologyExportImportService
):
    try:
        json_data, filename = service.export_network_topology(substation_id)
        return StreamingResponse(
            io.BytesIO(json_data.encode('utf-8')),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate json file.",
        ) from e
