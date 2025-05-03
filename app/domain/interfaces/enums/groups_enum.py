from enum import Enum


class Groups(Enum):
    Admin = 1
    User = 2
    Guest = 3

    def __str__(self):
        return self.name
