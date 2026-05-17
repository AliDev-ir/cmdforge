"""Shared utility functions for CmdForge."""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path


COMMAND_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def expand_path(value: str) -> Path:
    """Expand user and environment variables and return an absolute path."""
    return Path(os.path.expandvars(value)).expanduser().resolve()


def confirm(prompt: str, default: bool = False, assume_yes: bool = False) -> bool:
    """Ask a yes/no question."""
    if assume_yes:
        return True

    suffix = " [Y/n]: " if default else " [y/N]: "

    while True:
        answer = input(prompt + suffix).strip().lower()

        if not answer:
            return default

        if answer in {"y", "yes"}:
            return True

        if answer in {"n", "no"}:
            return False

        print("Please answer yes or no.")


def validate_command_name(name: str) -> tuple[bool, str]:
    """Validate a command name for safe wrapper creation."""
    if not name:
        return False, "Command name cannot be empty."

    if "/" in name:
        return False, "Command name must not contain slashes."

    if not COMMAND_NAME_RE.match(name):
        return (
            False,
            "Command name may only contain letters, numbers, dots, underscores, and hyphens.",
        )

    if name in {".", ".."}:
        return False, "Command name is not valid."

    return True, ""


def is_relative_to(child: Path, parent: Path) -> bool:
    """Compatibility helper for checking path containment."""
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def command_exists_in_path(name: str) -> str | None:
    """Return the existing command path if a command exists in PATH."""
    return shutil.which(name)


def print_section(title: str) -> None:
    print("")
    print(title)
    print("=" * len(title))
