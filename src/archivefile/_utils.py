from __future__ import annotations

import os
from pathlib import Path
from tarfile import is_tarfile
from typing import TYPE_CHECKING
from zipfile import is_zipfile

from archivefile._models import ArchiveMember

if TYPE_CHECKING:
    from archivefile._types import MemberLike, StrPath


def is_7zfile(file: StrPath) -> bool:
    try:
        import py7zr

        return py7zr.is_7zfile(file)  # type: ignore[arg-type]
    except ModuleNotFoundError:
        return False


def is_rarfile(file: StrPath) -> bool:
    try:
        import rarfile

        return rarfile.is_rarfile(file) or rarfile.is_rarfile_sfx(file)  # type: ignore[no-any-return]
    except ModuleNotFoundError:
        return False


def realpath(path: StrPath) -> Path:
    """
    Get the real path of a given file or directory.

    Parameters
    ----------
    path : str or Path
        A string representing a path or a Path object.

    Returns
    -------
    Path
        The path after expanding the user's home directory and resolving any symbolic links.

    """
    return Path(path).expanduser().resolve()


def is_archive(file: StrPath) -> bool:
    """
    Check whether the given archive file is a supported archive or not.

    Parameters
    ----------
    file : StrPath
        Path to the archive file.

    Returns
    -------
    bool
        True if the archive is supported, False otherwise.

    """
    file = realpath(file)

    if not file.is_file():
        return False

    return is_tarfile(file) or is_zipfile(file) or is_7zfile(file) or is_rarfile(file)


def get_member_name(member: MemberLike, /) -> str:
    """Get the member name from a string, path, or ArchiveMember."""

    match member:
        case str():
            return member

        case ArchiveMember():
            return member.name

        case os.PathLike():
            return Path(member).as_posix()

        case _:
            msg = (
                f"Unsupported type for 'member'. Expected 'str', 'PathLike', or 'ArchiveMember', "
                f"but got {type(member).__name__!r}."
            )
            raise TypeError(msg)
