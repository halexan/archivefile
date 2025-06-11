from __future__ import annotations

from pathlib import Path

import pytest

try:
    import py7zr as py7zr

    HAS_PY7ZR = True
except ModuleNotFoundError:
    HAS_PY7ZR = False

try:
    import rarfile as rarfile

    HAS_RARFILE = True
except ModuleNotFoundError:
    HAS_RARFILE = False

file_parametrizer = pytest.mark.parametrize(
    "file",
    [
        # --- Standard Files ---
        pytest.param(Path("tests/test_data/source_GNU.tar"), id="GNU.tar"),
        pytest.param(Path("tests/test_data/source_LZMA.zip"), id="LZMA.zip"),
        pytest.param(Path("tests/test_data/source_POSIX.tar.gz"), id="POSIX.tar.gz"),
        # --- Optional Files (conditionally skipped) ---
        pytest.param(
            Path("tests/test_data/source_LZMA.7z"),
            marks=pytest.mark.skipif(not HAS_PY7ZR, reason="py7zr is not installed."),
            id="LZMA.7z (optional)",
        ),
        pytest.param(
            Path("tests/test_data/source_BEST.rar"),
            marks=pytest.mark.skipif(not HAS_RARFILE, reason="rarfile is not installed."),
            id="BEST.rar (optional)",
        ),
    ],
)
