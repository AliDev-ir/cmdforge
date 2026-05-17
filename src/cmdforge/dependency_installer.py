"""Safe dependency installation helpers for CmdForge."""

from __future__ import annotations

import subprocess
from pathlib import Path

from cmdforge.dependency_detector import supported_install_files


def install_dependencies(venv_python: Path, dependency_files: list[Path]) -> None:
    """Install supported dependency files into the virtual environment."""
    supported = supported_install_files(dependency_files)

    if not supported:
        print("No supported dependency files to install.")
        return

    for dep_file in supported:
        print(f"Installing dependencies from: {dep_file}")
        subprocess.run(
            [
                str(venv_python),
                "-m",
                "pip",
                "install",
                "-r",
                str(dep_file),
            ],
            check=True,
        )
