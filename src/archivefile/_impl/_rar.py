from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from .._models import ArchiveMember
from .._utils import get_member_name, realpath
from ._abc import AbstractArchiveFile

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from rarfile import RarInfo

    from .._types import MemberLike, StrPath


def is_rarfile(file: StrPath) -> bool:
    try:
        import rarfile

        return rarfile.is_rarfile(file) or rarfile.is_rarfile_sfx(file)  # type: ignore[no-any-return]
    except ModuleNotFoundError:
        return False


class RarArchiveFile(AbstractArchiveFile):
    def __init__(self, file: StrPath, *, password: str | None = None) -> None:
        try:
            import rarfile
        except ModuleNotFoundError:
            filename = Path(file).as_posix()
            msg = (
                f"Cannot open archive: {filename!r}\n"
                "RAR support requires the 'rarfile' package, which is not installed.\n"
                "To enable RAR support, install archivefile with the optional RAR dependencies: 'archivefile[rar]'"
            )
            raise ModuleNotFoundError(msg) from None

        super().__init__(file, password=password)
        self._RarFile = rarfile.RarFile
        self._NoRarEntry = rarfile.NoRarEntry
        self._rarfile = self._RarFile(self._file)

    def get_member(self, member: MemberLike) -> ArchiveMember:
        name = get_member_name(member)

        try:
            # ZipFile and TarFile raise KeyError but RarFile raises it's own NoRarEntry
            # So for consistency's sake, we'll also raise KeyError here
            rarinfo: RarInfo = self._rarfile.getinfo(name)
        except self._NoRarEntry:
            msg = f"{name} not found in {self._file}"
            raise KeyError(msg) from None

        return ArchiveMember(
            name=rarinfo.filename,
            size=rarinfo.file_size,
            compressed_size=rarinfo.compress_size,
            datetime=datetime(*rarinfo.date_time),
            is_dir=rarinfo.filename.endswith("/"),
            is_file=not rarinfo.filename.endswith("/"),
        )

    def get_members(self) -> Iterator[ArchiveMember]:
        for rarinfo in self._rarfile.infolist():
            yield ArchiveMember(
                name=rarinfo.filename,
                size=rarinfo.file_size,
                compressed_size=rarinfo.compress_size,
                datetime=datetime(*rarinfo.date_time),
                is_dir=rarinfo.filename.endswith("/"),
                is_file=not rarinfo.filename.endswith("/"),
            )

    def get_names(self) -> tuple[str, ...]:
        return tuple(self._rarfile.namelist())

    def extract(self, member: MemberLike, *, destination: StrPath | None = None) -> Path:
        destination = realpath(destination) if destination else Path.cwd()
        destination.mkdir(parents=True, exist_ok=True)

        name = get_member_name(member)

        try:
            # ZipFile and TarFile raise KeyError but RarFile raises it's own NoRarEntry
            # So for consistency's sake, we'll also raise KeyError here
            self._rarfile.extract(member=name, path=destination, pwd=self._password)
        except self._NoRarEntry:
            msg = f"{name} not found in {self._file}"
            raise KeyError(msg) from None

        return destination / name

    def extractall(
        self,
        *,
        destination: StrPath | None = None,
        members: Iterable[MemberLike] | None = None,
    ) -> Path:
        destination = realpath(destination) if destination else Path.cwd()
        destination.mkdir(parents=True, exist_ok=True)

        names: set[str] = set()
        if members:
            all_members = self._rarfile.namelist()
            for member in members:
                name = get_member_name(member)
                if name in all_members:
                    names.add(name)
                else:
                    msg = f"{name} not found in {self._file}"
                    raise KeyError(msg)

        self._rarfile.extractall(path=destination, members=names, pwd=self._password)
        return destination

    def read_bytes(self, member: MemberLike) -> bytes:
        name = get_member_name(member)

        if name.endswith("/"):
            return b""

        try:
            # ZipFile and TarFile raise KeyError but RarFile raises it's own NoRarEntry
            # So for consistency's sake, we'll also raise KeyError here
            return self._rarfile.read(name, pwd=self._password)  # type: ignore[no-any-return]
        except self._NoRarEntry:
            msg = f"{name} not found in {self._file}"
            raise KeyError(msg) from None

    def close(self) -> None:
        self._rarfile.close()
