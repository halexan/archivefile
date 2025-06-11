from __future__ import annotations

import abc
from typing import TYPE_CHECKING

from archivefile._utils import realpath

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator
    from pathlib import Path

    from typing_extensions import Self

    from archivefile._models import ArchiveMember
    from archivefile._types import ErrorHandler, StrPath


class BaseArchiveAdapter(abc.ABC):
    """
    A base protocol that can be inherited from to implement more adapters.
    Refer to `src/archivefile/_core.py` for documentation of every method and property.
    """

    def __init__(self, file: StrPath, *, password: str | None = None) -> None:
        self._file = realpath(file)
        self._password = password

    @property
    def file(self) -> Path:
        return self._file

    @property
    def password(self) -> str | None:
        return self._password

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    @abc.abstractmethod
    def get_member(self, member: StrPath | ArchiveMember) -> ArchiveMember: ...

    @abc.abstractmethod
    def get_members(self) -> Iterator[ArchiveMember]: ...

    @abc.abstractmethod
    def get_names(self) -> tuple[str, ...]: ...

    @abc.abstractmethod
    def extract(self, member: StrPath | ArchiveMember, *, destination: StrPath | None = None) -> Path: ...

    @abc.abstractmethod
    def extractall(
        self,
        *,
        destination: StrPath | None = None,
        members: Iterable[StrPath | ArchiveMember] | None = None,
    ) -> Path: ...

    @abc.abstractmethod
    def read_bytes(self, member: StrPath | ArchiveMember) -> bytes: ...

    def read_text(
        self,
        member: StrPath | ArchiveMember,
        *,
        encoding: str = "utf-8",
        errors: ErrorHandler = "strict",
    ) -> str:
        return self.read_bytes(member).decode(encoding=encoding, errors=errors)

    @abc.abstractmethod
    def close(self) -> None: ...

    def __repr__(self) -> str:
        file = self.file.as_posix()
        cls = self.__class__.__name__
        if self.password:
            return f"{cls}({file!r}, password='********')"
        return f"{cls}({file!r})"
