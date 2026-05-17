"""Dependency file detection for CmdForge."""

from __future__ import annotations

from pathlib import Path


KNOWN_DEPENDENCY_FILES = (
    "requirements.txt",
    "requirements.clean.txt",
    "requirements-dev.txt",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "Pipfile",
    "Pipfile.lock",
    "poetry.lock",
)


def find_dependency_files(tool_dir: Path) -> list[Path]:
    """Find common dependency files in the root of a Python tool directory."""
    found: list[Path] = []

    for filename in KNOWN_DEPENDENCY_FILES:
        path = tool_dir / filename
        if path.is_file():
            found.append(path)

    extra_requirements = sorted(tool_dir.glob("requirements*.txt"))
    for path in extra_requirements:
        if path not in found:
            found.append(path)

    return found


def supported_install_files(files: list[Path]) -> list[Path]:
    """Return files CmdForge can safely install in the first release."""
    supported: list[Path] = []

    for path in files:
        if path.name.startswith("requirements") and path.suffix == ".txt":
            supported.append(path)

    return supported


def describe_dependency_files(files: list[Path]) -> None:
    """Print dependency file information."""
    if not files:
        print("No dependency files detected.")
        return

    print("Detected dependency files:")
    for path in files:
        print(f"- {path.name}")

    unsupported = [p for p in files if p not in supported_install_files(files)]
    if unsupported:
        print("")
        print("Note:")
        print("For v0.1, CmdForge installs requirements*.txt files only.")
        print("Other dependency files are detected but not installed automatically yet.")
