from typing import Protocol
from uuid import UUID, uuid4


def random_id() -> UUID:
    return uuid4()


class Tree(Protocol):
    id: UUID

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.id == other.id
        return False


    def __hash__(self):
        return hash(self.id)


class SourceFile(Tree, Protocol):
    source_path: str
