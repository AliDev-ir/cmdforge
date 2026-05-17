"""Virtual environment management for CmdForge."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def venv_path_for(tool_dir: Path) -> Path:
    return tool_dir / ".venv"


def venv_python_path(tool_dir: Path) -> Path:
    return venv_path_for(tool_dir) / "bin" / "python"


def create_venv(tool_dir: Path) -> Path:
    """Create .venv inside the target tool directory if it does not exist."""
    venv_dir = venv_path_for(tool_dir)
    python_path = venv_python_path(tool_dir)

    if python_path.is_file():
        print(f"Virtual environment already exists: {venv_dir}")
        return python_path

    print(f"Creating virtual environment: {venv_dir}")
    subprocess.run(
        [sys.executable, "-m", "venv", str(venv_dir)],
        check=True,
    )

    return python_path
