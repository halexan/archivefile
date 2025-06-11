from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from archivefile import ArchiveFile

from .helpers import file_parametrizer

if TYPE_CHECKING:
    from pathlib import Path


@file_parametrizer
def test_missing_member(file: Path) -> None:
    with pytest.raises(KeyError):
        with ArchiveFile(file) as archive:
            archive.get_member("non-existent.member")


@file_parametrizer
def test_missing_member_in_read_bytes(file: Path) -> None:
    with pytest.raises(KeyError):
        with ArchiveFile(file) as archive:
            archive.read_bytes("non-existent.member")


@file_parametrizer
def test_missing_member_in_read_text(file: Path) -> None:
    with pytest.raises(KeyError):
        with ArchiveFile(file) as archive:
            archive.read_text("non-existent.member")


@file_parametrizer
def test_missing_member_in_extract(file: Path) -> None:
    with pytest.raises(KeyError):
        with ArchiveFile(file) as archive:
            archive.extract("non-existent.member")


@file_parametrizer
def test_missing_member_in_extractall(file: Path, tmp_path: Path) -> None:
    with pytest.raises(KeyError):
        with ArchiveFile(file) as archive:
            archive.extractall(destination=tmp_path, members=["non-existent.member"])
