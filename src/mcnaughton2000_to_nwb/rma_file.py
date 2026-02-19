"""Parse McNaughton lab .RMA binary rate map files."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np


RMA_FILE_SIZE = 32768
MAP_SHAPE = (64, 64)
N_PIXELS = MAP_SHAPE[0] * MAP_SHAPE[1]  # 4096


@dataclass
class RmaFile:
    """Parsed contents of a single .RMA file."""

    path: Path
    rate_map: np.ndarray  # (64, 64) float32, firing rate in Hz
    occupancy_map: np.ndarray  # (64, 64) int32, bin visit counts

    # Derived from filename
    session_type: str
    cell_number: int | None  # None if not a CELL~N file

    @property
    def is_cell_map(self) -> bool:
        return self.cell_number is not None


def read_rma_file(path: Path) -> RmaFile:
    """Read and parse a single .RMA file.

    Format: 32768 bytes total
      - First 4096 float32 big-endian → rate map 64×64
      - Next 4096 int32 big-endian → occupancy map 64×64
    """
    data = path.read_bytes()
    if len(data) != RMA_FILE_SIZE:
        raise ValueError(f"{path}: expected {RMA_FILE_SIZE} bytes, got {len(data)}")

    rate_map = (
        np.frombuffer(data, dtype=">f4", count=N_PIXELS, offset=0)
        .reshape(MAP_SHAPE)
        .astype(np.float32, copy=False)
    )
    occupancy_map = (
        np.frombuffer(data, dtype=">i4", count=N_PIXELS, offset=N_PIXELS * 4)
        .reshape(MAP_SHAPE)
        .astype(np.int32, copy=False)
    )

    session_type, cell_number = _parse_rma_filename(path.name)

    return RmaFile(
        path=path,
        rate_map=rate_map,
        occupancy_map=occupancy_map,
        session_type=session_type,
        cell_number=cell_number,
    )


def _parse_rma_filename(name: str) -> tuple[str, int | None]:
    """Extract session type and cell number from RMA filename.

    Examples:
        ESCELL~1.RMA → ("ES", 1)
        MCCELL~3.RMA → ("MC", 3)
        ES2BC0~1.RMA → ("ES", None)   # not a per-cell map
    """
    upper = name.upper()

    cell_match = re.search(r"CELL~(\d+)", upper)
    cell_number = int(cell_match.group(1)) if cell_match else None

    if upper.startswith("ES"):
        session_type = "ES"
    elif upper.startswith("MC"):
        session_type = "MC"
    elif upper.startswith("BL"):
        session_type = "BL"
    else:
        session_type = "unknown"

    return session_type, cell_number
