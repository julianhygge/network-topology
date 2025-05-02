import enum


class HyggeBaseEnum(enum.Enum):
    def __str__(self):
        return self.value

    def __repr__(self):
        return str(self.value)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)
