from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest

from archivefile import ArchiveFile, UnsupportedArchiveFormatError

if TYPE_CHECKING:
    from pathlib import Path


def test_non_existent_file_error(tmp_path: Path) -> None:
    archive_path = tmp_path / "foo.zip"
    with pytest.raises(FileNotFoundError, match=re.escape(str(archive_path))):
        ArchiveFile(archive_path)


def test_unsupported_archive_format_error(tmp_path: Path) -> None:
    archive_path = tmp_path / "foo.zip"
    archive_path.write_text("This is not a valid archive format.")
    filename = archive_path.as_posix()
    message = (
        f"Unsupported or unrecognized archive format for file: {filename!r}.\n"
        "If this is a 7z or rar archive, support is available via the optional "
        "extras 'archivefile[7z]' and 'archivefile[rar]'."
    )
    with pytest.raises(UnsupportedArchiveFormatError, match=re.escape(message)):
        ArchiveFile(archive_path)


def test_missing_member(archive_file: ArchiveFile) -> None:
    with pytest.raises(KeyError):
        archive_file.get_member("non-existent.member")


def test_missing_member_in_read_bytes(archive_file: ArchiveFile) -> None:
    with pytest.raises(KeyError):
        archive_file.read_bytes("non-existent.member")


def test_missing_member_in_read_text(archive_file: ArchiveFile) -> None:
    with pytest.raises(KeyError):
        archive_file.read_text("non-existent.member")


def test_missing_member_in_extract(archive_file: ArchiveFile) -> None:
    with pytest.raises(KeyError):
        archive_file.extract("non-existent.member")


def test_missing_member_in_extractall(archive_file: ArchiveFile, tmp_path: Path) -> None:
    with pytest.raises(KeyError):
        archive_file.extractall(destination=tmp_path, members=["non-existent.member"])
