from enum import Enum


class LoadProfileStrategy(Enum):
    Linear = "Linear"
    Spline = "Spline"
    PChip = "PChip"
    Akima1D = "Akima1D"
