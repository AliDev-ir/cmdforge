"""Wrapper creation, metadata, and rollback helpers for CmdForge."""

from __future__ import annotations

import os
import shlex
import stat
import time
from pathlib import Path

from cmdforge.utils import command_exists_in_path


MANAGED_MARKER = "Managed by CmdForge."


def default_user_bin_dir() -> Path:
    return Path.home() / ".local" / "bin"


def system_bin_dir() -> Path:
    return Path("/usr/local/bin")


def build_wrapper_content(
    python_executable: Path | None,
    entry_file: Path,
    command_name: str | None = None,
    scope: str | None = None,
) -> str:
    """Build a safe bash wrapper script with CmdForge metadata."""
    quoted_entry = shlex.quote(str(entry_file))

    if python_executable is not None:
        quoted_python = shlex.quote(str(python_executable))
        python_display = str(python_executable)
        exec_line = f'exec {quoted_python} {quoted_entry} "$@"'
    else:
        python_display = "/usr/bin/env python3"
        exec_line = f'exec /usr/bin/env python3 {quoted_entry} "$@"'

    return "\n".join(
        [
            "#!/usr/bin/env bash",
            f"# {MANAGED_MARKER}",
            f"# Command name: {command_name or 'unknown'}",
            f"# Scope: {scope or 'unknown'}",
            f"# Entry file: {entry_file}",
            f"# Python executable: {python_display}",
            exec_line,
            "",
        ]
    )


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
    scope: str | None = None,
) -> Path:
    """Create the command wrapper."""
    target = install_dir / command_name
    content = build_wrapper_content(
        python_executable=python_executable,
        entry_file=entry_file,
        command_name=command_name,
        scope=scope,
    )

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


def is_cmdforge_wrapper(path: Path) -> bool:
    """Return True if a wrapper appears to be managed by CmdForge."""
    if not path.is_file():
        return False

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False

    return MANAGED_MARKER in content


def read_wrapper_metadata(path: Path) -> dict[str, str]:
    """Read simple '# Key: value' metadata from a CmdForge wrapper."""
    metadata: dict[str, str] = {}

    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return metadata

    for line in lines:
        if not line.startswith("# "):
            continue

        body = line[2:]
        if ": " not in body:
            continue

        key, value = body.split(": ", 1)
        metadata[key.strip()] = value.strip()

    return metadata


def detected_venv_from_metadata(metadata: dict[str, str]) -> Path | None:
    """Detect a .venv directory from wrapper metadata."""
    python_value = metadata.get("Python executable")
    if not python_value:
        return None

    python_path = Path(python_value)
    parts = python_path.parts

    if ".venv" not in parts:
        return None

    venv_index = parts.index(".venv")
    venv_path = Path(*parts[: venv_index + 1])

    if (venv_path / "pyvenv.cfg").is_file():
        return venv_path

    return None


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
