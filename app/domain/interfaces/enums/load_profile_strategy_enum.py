from enum import Enum


class LoadProfileStrategy(Enum):
    Linear = "Linear"
    Spline = "Spline"
    PChip = "PChip"
