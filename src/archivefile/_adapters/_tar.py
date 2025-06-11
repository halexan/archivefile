from __future__ import annotations

import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from archivefile._adapters._base import BaseArchiveAdapter
from archivefile._models import ArchiveMember
from archivefile._utils import get_member_name, realpath

if TYPE_CHECKING:
    from collections.abc import Iterable

    from typing_extensions import Generator

    from archivefile._types import StrPath


class TarFileAdapter(BaseArchiveAdapter):
    def __init__(self, file: StrPath, *, password: str | None = None) -> None:
        super().__init__(file, password=password)
        self._tarfile = tarfile.TarFile.open(self.file)
        # https://docs.python.org/3/library/tarfile.html#supporting-older-python-versions
        self._tarfile.extraction_filter = getattr(tarfile, "data_filter", (lambda member, path: member))

    def get_member(self, member: StrPath | ArchiveMember) -> ArchiveMember:
        name = get_member_name(member)
        tarinfo = self._tarfile.getmember(name)

        return ArchiveMember(
            name=tarinfo.name,
            size=tarinfo.size,
            compressed_size=tarinfo.size,
            datetime=datetime.fromtimestamp(tarinfo.mtime, tz=timezone.utc),
            is_dir=tarinfo.isdir(),
            is_file=tarinfo.isfile(),
        )

    def get_members(self) -> Generator[ArchiveMember]:
        for tarinfo in self._tarfile.getmembers():
            yield ArchiveMember(
                name=tarinfo.name,
                size=tarinfo.size,
                compressed_size=tarinfo.size,
                datetime=datetime.fromtimestamp(tarinfo.mtime, tz=timezone.utc),
                is_dir=tarinfo.isdir(),
                is_file=tarinfo.isfile(),
            )

    def get_names(self) -> tuple[str, ...]:
        return tuple(self._tarfile.getnames())

    def extract(self, member: StrPath | ArchiveMember, *, destination: StrPath | None = None) -> Path:
        destination = realpath(destination) if destination else Path.cwd()
        destination.mkdir(parents=True, exist_ok=True)

        name = get_member_name(member)
        self._tarfile.extract(member=name, path=destination)

        return destination / name

    def extractall(
        self,
        *,
        destination: StrPath | None = None,
        members: Iterable[StrPath | ArchiveMember] | None = None,
    ) -> Path:
        destination = realpath(destination) if destination else Path.cwd()
        destination.mkdir(parents=True, exist_ok=True)

        if members:
            names = [self._tarfile.getmember(get_member_name(member)) for member in members]
            self._tarfile.extractall(path=destination, members=names)
        else:
            self._tarfile.extractall(path=destination)

        return destination

    def read_bytes(self, member: StrPath | ArchiveMember) -> bytes:
        name = get_member_name(member)
        fileobj = self._tarfile.extractfile(name)
        if fileobj is None:  # pragma: no cover
            return b""
        return fileobj.read()

    def close(self) -> None:
        self._tarfile.close()
