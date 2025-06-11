from __future__ import annotations

from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile

from archivefile import ArchiveFile

from .helpers import file_parametrizer


@file_parametrizer
def test_extract(file: Path, tmp_path: Path) -> None:
    with ArchiveFile(file) as archive:
        member = archive.extract("pyanilist-main/README.md", destination=tmp_path)
        assert member.is_file()


@file_parametrizer
def test_extract_without_context_manager(file: Path, tmp_path: Path) -> None:
    archive = ArchiveFile(file)
    extracted_file = archive.extract("pyanilist-main/README.md", destination=tmp_path)
    archive.close()
    assert extracted_file.is_file()


@file_parametrizer
def test_extract_by_member(file: Path, tmp_path: Path) -> None:
    with ArchiveFile(file) as archive:
        member = next(member for member in archive.get_members() if member.is_file)
        outfile = archive.extract(member, destination=tmp_path)
        assert outfile.is_file()


@file_parametrizer
def test_extractall(file: Path, tmp_path: Path) -> None:
    with ZipFile("tests/test_data/source_LZMA.zip") as archive:
        dest = tmp_path / uuid4().hex
        archive.extractall(path=dest)
        control = tuple((dest / "pyanilist-main").rglob("*"))

    with ArchiveFile(file) as archive:
        dest2 = tmp_path / uuid4().hex
        archive.extractall(destination=dest2)
        members = tuple((dest / "pyanilist-main").rglob("*"))
        assert control == members


@file_parametrizer
def test_extractall_by_members(file: Path, tmp_path: Path) -> None:
    expected = [
        "pyanilist-main/.gitignore",
        "pyanilist-main/.pre-commit-config.yaml",
        "pyanilist-main/poetry.lock",
        "pyanilist-main/pyproject.toml",
    ]

    members: list[str | Path] = [
        "pyanilist-main/.gitignore",
        Path("pyanilist-main/.pre-commit-config.yaml"),
        "pyanilist-main/poetry.lock",
        "pyanilist-main/pyproject.toml",
    ]

    with ArchiveFile(file) as archive:
        folder = archive.extractall(destination=tmp_path, members=members) / "pyanilist-main"
        assert len(members) == len(tuple(folder.rglob("*"))) == 4
        assert sorted(expected) == sorted([member.relative_to(tmp_path).as_posix() for member in folder.rglob("*")])
