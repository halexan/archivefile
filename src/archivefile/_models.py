from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import datetime as dt


@dataclass(frozen=True, kw_only=True, slots=True)
class ArchiveMember:
    """
    Represents a member of an archive file.
    """

    name: str
    """Name of the archive member."""

    size: int
    """Uncompressed size of the archive member."""

    compressed_size: int
    """Compressed size of the archive member."""

    datetime: dt.datetime
    """The time and date of the last modification to the archive member."""

    is_dir: bool
    """True if the archive member is a directory, False otherwise."""

    is_file: bool
    """True if the archive member is a file, False otherwise."""

    def __str__(self) -> str:
        return self.name
