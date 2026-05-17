"""Remove CmdForge-managed command wrappers."""

from __future__ import annotations

import os
import shutil
from argparse import Namespace
from pathlib import Path

from cmdforge.utils import confirm, expand_path, print_section, validate_command_name
from cmdforge.wrapper_manager import (
    default_user_bin_dir,
    detected_venv_from_metadata,
    is_cmdforge_wrapper,
    read_wrapper_metadata,
    system_bin_dir,
)


def resolve_remove_target(args: Namespace) -> tuple[Path, str]:
    """Resolve install directory and scope for command removal."""
    if getattr(args, "system", False) and getattr(args, "scope", None) == "user":
        raise ValueError("--system conflicts with --scope user.")

    if getattr(args, "install_dir", None):
        return expand_path(args.install_dir), "custom"

    if getattr(args, "system", False):
        return system_bin_dir(), "system"

    scope = getattr(args, "scope", None) or "user"

    if scope == "system":
        return system_bin_dir(), "system"

    return default_user_bin_dir(), "user"


def remove_venv_if_requested(
    venv_dir: Path | None,
    assume_yes: bool,
    remove_venv: bool,
) -> None:
    """Remove a detected venv only when requested."""
    if not remove_venv:
        if venv_dir is not None:
            print("")
            print("Detected virtual environment:")
            print(f"  {venv_dir}")
            print("It was not removed. Use --remove-venv if you want to remove it.")
        return

    if venv_dir is None:
        print("")
        print("No CmdForge-managed .venv was detected from wrapper metadata.")
        return

    active_venv = os.environ.get("VIRTUAL_ENV")
    if active_venv and Path(active_venv).resolve() == venv_dir.resolve():
        raise RuntimeError(
            "Refusing to remove the currently active virtual environment. "
            "Deactivate it first."
        )

    if not confirm(f"Remove virtual environment {venv_dir}?", default=False, assume_yes=assume_yes):
        print("Virtual environment was not removed.")
        return

    shutil.rmtree(venv_dir)
    print(f"Removed virtual environment: {venv_dir}")


def run_command_remover(args: Namespace) -> int:
    """Remove a CmdForge-managed command wrapper."""
    print_section("CmdForge remove")

    command_name = args.name
    ok, message = validate_command_name(command_name)
    if not ok:
        raise ValueError(message)

    install_dir, scope = resolve_remove_target(args)
    target = install_dir / command_name

    print(f"Command name:      {command_name}")
    print(f"Scope:             {scope}")
    print(f"Install directory: {install_dir}")
    print(f"Target wrapper:    {target}")

    if not target.exists():
        print("")
        print("Command wrapper not found.")
        return 1

    managed = is_cmdforge_wrapper(target)
    metadata = read_wrapper_metadata(target)
    venv_dir = detected_venv_from_metadata(metadata)

    print("")
    print(f"Managed by CmdForge: {'yes' if managed else 'no'}")

    if metadata:
        print("Wrapper metadata:")
        for key, value in metadata.items():
            print(f"- {key}: {value}")

    if not managed and not getattr(args, "force", False):
        print("")
        print("Refusing to remove this file because it is not marked as a CmdForge wrapper.")
        print("Use --force only if you are sure this is safe.")
        return 1

    if not confirm(f"Remove wrapper {target}?", default=False, assume_yes=args.yes):
        print("Aborted.")
        return 1

    target.unlink()
    print("")
    print(f"Removed wrapper: {target}")

    remove_venv_if_requested(
        venv_dir=venv_dir,
        assume_yes=args.yes,
        remove_venv=args.remove_venv,
    )

    return 0
