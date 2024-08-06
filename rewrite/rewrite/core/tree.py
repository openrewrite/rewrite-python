from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Optional, Union, List
from uuid import UUID, uuid4

import datetime


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
    source_path: Path


@dataclass(frozen=True)
class FileAttributes:
    creation_time: Optional[datetime]
    last_modified_time: Optional[datetime]
    last_access_time: Optional[datetime]
    is_readable: bool
    is_writable: bool
    is_executable: bool
    size: int

    @staticmethod
    def from_path(path: Path) -> Optional[FileAttributes]:
        if path.exists():
            try:
                # Get file stats
                stat = path.stat()
                creation_time = datetime.fromtimestamp(stat.st_ctime)
                last_modified_time = datetime.fromtimestamp(stat.st_mtime)
                last_access_time = datetime.fromtimestamp(stat.st_atime)

                is_readable = os.access(path, os.R_OK)
                is_writable = os.access(path, os.W_OK)
                is_executable = os.access(path, os.X_OK)
                size = stat.st_size

                return FileAttributes(creation_time, last_access_time, last_modified_time, is_readable, is_writable,
                                      is_executable, size)
            except OSError:
                pass
        return None


@dataclass(frozen=True)
class Checksum:
    algorithm: str
    value: bytes
