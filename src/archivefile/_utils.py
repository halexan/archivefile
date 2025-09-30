from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from archivefile._models import ArchiveMember

if TYPE_CHECKING:
    from archivefile._types import MemberLike, StrPath


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
