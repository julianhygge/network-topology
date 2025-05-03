from app.domain.interfaces.enums.hygge_base_enum import HyggeBaseEnum


class LoadProfileStrategy(HyggeBaseEnum):
    Linear = "Linear"
    Spline = "Spline"
    PChip = "PChip"
    Akima1D = "Akima1D"
