from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING
from zipfile import ZipFile

from .._models import ArchiveMember
from .._utils import get_member_name, realpath
from ._abc import AbstractArchiveFile

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from .._types import MemberLike, StrPath


class ZipArchiveFile(AbstractArchiveFile):
    def __init__(self, file: StrPath, *, password: str | None = None) -> None:
        super().__init__(file, password=password)
        self._encoded_password = password.encode() if password else None
        self._zipfile = ZipFile(self.file)

    def get_member(self, member: MemberLike) -> ArchiveMember:
        name = get_member_name(member)
        zipinfo = self._zipfile.getinfo(name)

        return ArchiveMember(
            name=zipinfo.filename,
            size=zipinfo.file_size,
            compressed_size=zipinfo.compress_size,
            datetime=datetime(*zipinfo.date_time),
            is_dir=zipinfo.is_dir(),
            is_file=not zipinfo.is_dir(),
        )

    def get_members(self) -> Iterator[ArchiveMember]:
        for zipinfo in self._zipfile.filelist:
            yield ArchiveMember(
                name=zipinfo.filename,
                size=zipinfo.file_size,
                compressed_size=zipinfo.compress_size,
                datetime=datetime(*zipinfo.date_time),
                is_dir=zipinfo.is_dir(),
                is_file=not zipinfo.is_dir(),
            )

    def get_names(self) -> tuple[str, ...]:
        return tuple(self._zipfile.namelist())

    def extract(self, member: MemberLike, *, destination: StrPath | None = None) -> Path:
        destination = realpath(destination) if destination else Path.cwd()
        destination.mkdir(parents=True, exist_ok=True)

        name = get_member_name(member)
        self._zipfile.extract(member=name, path=destination, pwd=self._encoded_password)

        return destination / name

    def extractall(
        self,
        *,
        destination: StrPath | None = None,
        members: Iterable[MemberLike] | None = None,
    ) -> Path:
        destination = realpath(destination) if destination else Path.cwd()
        destination.mkdir(parents=True, exist_ok=True)

        if members:
            names = [get_member_name(member) for member in members]
            self._zipfile.extractall(path=destination, members=names, pwd=self._encoded_password)
        else:
            self._zipfile.extractall(path=destination, pwd=self._encoded_password)

        return destination

    def read_bytes(self, member: MemberLike) -> bytes:
        name = get_member_name(member)
        return self._zipfile.read(name, pwd=self._encoded_password)

    def close(self) -> None:
        self._zipfile.close()
