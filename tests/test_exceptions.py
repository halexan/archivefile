from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from archivefile import ArchiveFile


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
