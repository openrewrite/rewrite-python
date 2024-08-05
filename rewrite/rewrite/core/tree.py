from typing import Protocol
from uuid import UUID, uuid4


def random_id() -> UUID:
    return uuid4()


class Tree(Protocol):
    id: UUID


class SourceFile(Tree, Protocol):
    sourcePath: str
