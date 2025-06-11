from __future__ import annotations

import io
from pathlib import Path
from typing import TYPE_CHECKING

from py7zr import FileInfo, SevenZipFile
from py7zr.io import Py7zIO, WriterFactory

from archivefile._adapters._base import BaseArchiveAdapter
from archivefile._models import ArchiveMember
from archivefile._utils import get_member_name, realpath

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from archivefile._types import StrPath


class Py7zBytesIO(Py7zIO):
    def __init__(self, filename: str):
        self.filename = filename
        self._buffer = io.BytesIO()

    def write(self, s: bytes | bytearray) -> int:
        return self._buffer.write(s)

    def read(self, size: int | None = None) -> bytes:
        return self._buffer.read()

    def seek(self, offset: int, whence: int = 0) -> int:
        return self._buffer.seek(offset, whence)

    def flush(self) -> None:
        return self._buffer.flush()

    def size(self) -> int:
        return self._buffer.getbuffer().nbytes


class BytesIOFactory(WriterFactory):
    def __init__(self) -> None:
        self.products: dict[str, Py7zBytesIO] = {}

    def create(self, filename: str) -> Py7zIO:
        product = Py7zBytesIO(filename)
        self.products[filename] = product
        return product

    def read(self, filename: str) -> bytes:
        try:
            return self.products[filename].read()
        except KeyError:
            return b""


class SevenZipFileAdapter(BaseArchiveAdapter):
    def __init__(self, file: StrPath, *, password: str | None = None) -> None:
        super().__init__(file, password=password)
        self._sevenzipfile = SevenZipFile(self.file, password=self.password)

    def get_member(self, member: StrPath | ArchiveMember) -> ArchiveMember:
        name = get_member_name(member).removesuffix("/")
        try:
            # SevenZipFile doesn't have an equivalent for `get_member` like the rest, so we hand craft it instead
            sevenzipinfo: FileInfo = next(member for member in self._sevenzipfile.list() if member.filename == name)
        except StopIteration:
            # ZipFile and TarFile raise KeyError
            # So for consistency, we'll also raise KeyError here
            msg = f"{name} not found in {self.file}"
            raise KeyError(msg) from None

        return ArchiveMember(
            name=sevenzipinfo.filename,
            size=sevenzipinfo.uncompressed,
            # Sometimes sevenzip can return 0 for compressed size when there's no compression
            # in that case we simply return the uncompressed size instead.
            compressed_size=sevenzipinfo.compressed or sevenzipinfo.uncompressed,
            datetime=sevenzipinfo.creationtime,
            is_dir=sevenzipinfo.is_directory,
            is_file=not sevenzipinfo.is_directory,
        )

    def get_members(self) -> Iterator[ArchiveMember]:
        for sevenzipinfo in self._sevenzipfile.list():
            yield ArchiveMember(
                name=sevenzipinfo.filename,
                size=sevenzipinfo.uncompressed,
                # Sometimes sevenzip can return 0 for compressed size when there's no compression
                # in that case we simply return the uncompressed size instead.
                compressed_size=sevenzipinfo.compressed or sevenzipinfo.uncompressed,
                datetime=sevenzipinfo.creationtime,
                is_dir=sevenzipinfo.is_directory,
                is_file=not sevenzipinfo.is_directory,
            )

    def get_names(self) -> tuple[str, ...]:
        return tuple(self._sevenzipfile.getnames())

    def extract(self, member: StrPath | ArchiveMember, *, destination: StrPath | None = None) -> Path:
        destination = realpath(destination) if destination else Path.cwd()
        destination.mkdir(parents=True, exist_ok=True)
        name = get_member_name(member)

        if name in self.get_names():
            self._sevenzipfile.extract(path=destination, targets=[name], recursive=True)
        else:
            # ZipFile and TarFile raise KeyError but SevenZipFile does nothing
            # So for consistency's sake, we'll also raise KeyError here
            msg = f"{name} not found in {self.file}"
            raise KeyError(msg)

        self._sevenzipfile.reset()
        return destination / name

    def extractall(
        self,
        *,
        destination: StrPath | None = None,
        members: Iterable[StrPath | ArchiveMember] | None = None,
    ) -> Path:
        destination = realpath(destination) if destination else Path.cwd()
        destination.mkdir(parents=True, exist_ok=True)

        names: set[str] = set()
        if members:
            all_members = self._sevenzipfile.getnames()
            for member in members:
                if (name := get_member_name(member)) in all_members:
                    names.add(name)
                else:
                    msg = f"{name} not found in {self.file}"
                    raise KeyError(msg)

        if names:
            self._sevenzipfile.extract(path=destination, targets=names, recursive=True)
        else:
            self._sevenzipfile.extractall(path=destination)

        self._sevenzipfile.reset()
        return destination

    def read_bytes(self, member: StrPath | ArchiveMember) -> bytes:
        name = get_member_name(member).removesuffix("/")

        if name not in self._sevenzipfile.getnames():
            msg = f"{name} not found in {self._file}"
            raise KeyError(msg)

        factory = BytesIOFactory()
        self._sevenzipfile.extract(targets=[name], factory=factory)
        self._sevenzipfile.reset()
        return factory.read(name)

    def close(self) -> None:
        self._sevenzipfile.close()  # type: ignore[no-untyped-call]
