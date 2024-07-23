from enum import Enum


class LoadSource(Enum):
    File = "File"
    Template = "Template"
    Engine = "Engine"
    Builder = "Builder"

    def __str__(self):
        return str(self.name)
