from __future__ import annotations

from typing import TYPE_CHECKING

from archivefile import ArchiveFile

from .helpers import file_parametrizer

if TYPE_CHECKING:
    from pathlib import Path


@file_parametrizer
def test_get_members(file: Path) -> None:
    with ArchiveFile(file) as archive:
        assert len(tuple(archive.get_members())) == 53


@file_parametrizer
def test_get_members_without_context_manager(file: Path) -> None:
    archive = ArchiveFile(file)
    total_members = len(tuple(archive.get_members()))
    archive.close()
    assert total_members == 53


@file_parametrizer
def test_get_names(file: Path) -> None:
    with ArchiveFile(file) as archive:
        assert len(archive.get_names()) == 53


@file_parametrizer
def test_get_names_without_context_manager(file: Path) -> None:
    archive = ArchiveFile(file)
    total_members = len(archive.get_names())
    archive.close()
    assert total_members == 53


@file_parametrizer
def test_member_and_names(file: Path) -> None:
    with ArchiveFile(file) as archive:
        names = tuple([member.name for member in archive.get_members()])
        assert archive.get_names() == names


@file_parametrizer
def test_members_and_names_without_context_manager(file: Path) -> None:
    archive = ArchiveFile(file)
    names = tuple([member.name for member in archive.get_members()])
    assert archive.get_names() == names
    archive.close()


@file_parametrizer
def test_get_member_files(file: Path) -> None:
    with ArchiveFile(file) as archive:
        assert archive.file == file.resolve()
        assert archive.password is None

        member = archive.get_member("pyanilist-main/README.md")
        assert member.name == "pyanilist-main/README.md"
        assert member.size == 3799
        assert member.is_dir is False
        assert member.is_file is True


@file_parametrizer
def test_get_member_dirs(file: Path) -> None:
    with ArchiveFile(file) as archive:
        assert archive.file == file.resolve()
        assert archive.password is None

        member = archive.get_member("pyanilist-main/docs/")
        assert member.size == 0
        assert member.compressed_size == 0
        assert member.is_dir is True
        assert member.is_file is False
