"""Service for managing load profile builder items."""

from typing import Any, List, Tuple
from uuid import UUID

from app.data.interfaces.load.i_load_load_profile_repository import (
    ILoadProfileRepository,
)
from app.data.interfaces.load.i_load_profile_builder_repository import (
    ILoadProfileBuilderRepository,
)
from app.domain.interfaces.enums.load_source_enum import LoadSource


class LoadProfileBuilderService:
    """
    Service responsible for managing the creation, update, deletion,
    and retrieval of load profile items created via the builder.
    """

    def __init__(
        self,
        load_profile_repo: ILoadProfileRepository,
        load_profile_builder_repo: ILoadProfileBuilderRepository,
    ):
        self._load_profile_repo = load_profile_repo
        self._load_profile_builder_repository = load_profile_builder_repo

    def save_load_profile_items(
        self, user_id: UUID, house_id: UUID, items: List[dict]
    ) -> Tuple[List[Any], UUID]:  # Assuming List[LoadProfileBuilderItem]
        """
        Saves (creates, updates, or deletes) load profile items for a given
        house and user.
        """
        load_profile = self._load_profile_repo.get_or_create_by_house_id(
            user_id, house_id, LoadSource.Builder.value
        )
        profile_id = load_profile.id

        existing_items = (
            self._load_profile_builder_repository.get_items_by_profile_id(
                profile_id
            )
        )
        existing_ids = {item.id for item in existing_items}

        to_create = []
        to_update = []
        processed_ids = set()

        for item_data in items:
            item_data["profile_id"] = profile_id
            item_id = item_data.get("id")

            if item_id and item_id in existing_ids:
                to_update.append(item_data)
                processed_ids.add(item_id)
            else:
                item_data.pop("id", None)
                item_data["modified_by"] = user_id
                item_data["created_by"] = user_id
                to_create.append(item_data)

        ids_to_delete = existing_ids - processed_ids

        if ids_to_delete:
            for item_id_to_delete in ids_to_delete:
                self._load_profile_builder_repository.delete(item_id_to_delete)
        if to_create:
            self._load_profile_builder_repository.create_items_in_bulk(
                to_create
            )
        if to_update:
            self._load_profile_builder_repository.update_items_in_bulk(
                to_update
            )

        # Fetch and return all current items for the profile
        current_items = (
            self._load_profile_builder_repository.get_items_by_profile_id(
                profile_id
            )
        )
        return current_items, profile_id

    def get_load_profile_builder_items(
        self, user_id: UUID, house_id: UUID
    ) -> Tuple[List[Any], UUID]:  # Assuming List[LoadProfileBuilderItem]
        """
        Retrieves load profile builder items for a given house and user.
        If no profile exists for the builder source, one is created.
        """
        load_profile = self._load_profile_repo.get_or_create_by_house_id(
            user_id, house_id, LoadSource.Builder.value
        )
        # Assuming get_items_by_profile_id takes profile_id (UUID)
        items = self._load_profile_builder_repository.get_items_by_profile_id(
            load_profile.id
        )
        return items, load_profile.id
