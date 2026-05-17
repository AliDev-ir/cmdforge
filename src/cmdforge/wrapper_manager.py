"""Wrapper creation and rollback helpers for CmdForge."""

from __future__ import annotations

import os
import shlex
import stat
import time
from pathlib import Path

from cmdforge.utils import command_exists_in_path


def default_user_bin_dir() -> Path:
    return Path.home() / ".local" / "bin"


def system_bin_dir() -> Path:
    return Path("/usr/local/bin")


def build_wrapper_content(python_executable: Path | None, entry_file: Path) -> str:
    """Build a safe bash wrapper script."""
    quoted_entry = shlex.quote(str(entry_file))

    if python_executable is not None:
        quoted_python = shlex.quote(str(python_executable))
        exec_line = f"exec {quoted_python} {quoted_entry} \"$@\""
    else:
        exec_line = f"exec /usr/bin/env python3 {quoted_entry} \"$@\""

    return f"#!/usr/bin/env bash\n{exec_line}\n"


def ensure_bin_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def path_contains_dir(path: Path) -> bool:
    path_string = os.environ.get("PATH", "")
    entries = [Path(p).expanduser() for p in path_string.split(os.pathsep) if p]
    return path.expanduser() in entries


def create_wrapper(
    command_name: str,
    entry_file: Path,
    install_dir: Path,
    python_executable: Path | None,
    overwrite: bool = False,
    dry_run: bool = False,
) -> Path:
    """Create the command wrapper."""
    target = install_dir / command_name
    content = build_wrapper_content(python_executable, entry_file)

    existing_in_path = command_exists_in_path(command_name)
    if existing_in_path and Path(existing_in_path).resolve() != target.resolve():
        print(f"Warning: command already exists in PATH: {existing_in_path}")

    if target.exists() and not overwrite:
        raise FileExistsError(f"Target command already exists: {target}")

    if dry_run:
        print("")
        print("Dry-run wrapper target:")
        print(target)
        print("")
        print("Dry-run wrapper content:")
        print(content)
        return target

    ensure_bin_dir(install_dir)

    if target.exists():
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        backup = target.with_name(f"{target.name}.bak.{timestamp}")
        target.rename(backup)
        print(f"Existing wrapper backed up to: {backup}")

    target.write_text(content, encoding="utf-8")

    current_mode = target.stat().st_mode
    target.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    return target


def print_path_hint(install_dir: Path) -> None:
    if path_contains_dir(install_dir):
        return

    print("")
    print("PATH notice:")
    print(f"{install_dir} is not currently in PATH.")
    print("Add this line to your shell config if needed:")
    print(f'export PATH="{install_dir}:$PATH"')


def print_rollback(command_path: Path, venv_dir: Path | None) -> None:
    print("")
    print("Rollback:")
    print(f"rm -f {shlex.quote(str(command_path))}")

    if venv_dir is not None:
        print(f"rm -rf {shlex.quote(str(venv_dir))}")
