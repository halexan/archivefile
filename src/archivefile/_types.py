from __future__ import annotations

import os
from typing import Literal, TypeAlias

StrPath: TypeAlias = str | os.PathLike[str]
ErrorHandler: TypeAlias = Literal[
    "strict", "ignore", "replace", "backslashreplace", "surrogateescape", "xmlcharrefreplace", "namereplace"
]
