from app.domain.interfaces.enums.hygge_base_enum import HyggeBaseEnum


class WorkProfileType(str, HyggeBaseEnum):
    """Enum for different types of work profiles."""

    WORKS_AT_HOME = "works_at_home"
    DAY_WORKER_OUTSIDE = "day_worker_outside"
    NIGHT_WORKER_OUTSIDE = "night_worker_outside"
    UNSPECIFIED = "unspecified"
