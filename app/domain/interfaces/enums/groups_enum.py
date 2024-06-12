from enum import Enum


class Groups(Enum):
    Admin = 1
    Consumer = 2
    Guest = 4
    Pending = 5

    def __str__(self):
        return self.name
