from __future__ import annotations

import abc
from typing import TYPE_CHECKING

from archivefile._utils import realpath

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator
    from pathlib import Path

    from typing_extensions import Self

    from archivefile._models import ArchiveMember
    from archivefile._types import ErrorHandler, MemberLike, StrPath


class AbstractArchiveFile(abc.ABC):
    def __init__(self, file: StrPath, *, password: str | None = None) -> None:
        self._file = realpath(file)
        self._password = password
        super().__init__()

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
    def get_member(self, member: MemberLike) -> ArchiveMember: ...

    @abc.abstractmethod
    def get_members(self) -> Iterator[ArchiveMember]: ...

    @abc.abstractmethod
    def get_names(self) -> tuple[str, ...]: ...

    @abc.abstractmethod
    def extract(self, member: MemberLike, *, destination: StrPath | None = None) -> Path: ...

    @abc.abstractmethod
    def extractall(
        self,
        *,
        destination: StrPath | None = None,
        members: Iterable[MemberLike] | None = None,
    ) -> Path: ...

    @abc.abstractmethod
    def read_bytes(self, member: MemberLike) -> bytes: ...

    def read_text(
        self,
        member: MemberLike,
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
