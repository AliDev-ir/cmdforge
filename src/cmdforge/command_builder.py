"""Command-builder workflow for CmdForge."""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from cmdforge.dependency_detector import (
    describe_dependency_files,
    find_dependency_files,
)
from cmdforge.dependency_installer import install_dependencies
from cmdforge.utils import (
    command_exists_in_path,
    confirm,
    expand_path,
    is_relative_to,
    print_section,
    validate_command_name,
)
from cmdforge.venv_manager import create_venv, venv_path_for, venv_python_path
from cmdforge.wrapper_manager import (
    create_wrapper,
    default_user_bin_dir,
    print_path_hint,
    print_rollback,
    system_bin_dir,
)


IGNORED_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
}


def find_python_entry_candidates(tool_dir: Path) -> list[Path]:
    """Find likely Python entry files."""
    candidates: list[Path] = []

    for path in tool_dir.rglob("*.py"):
        if any(part in IGNORED_DIR_NAMES for part in path.parts):
            continue

        if not path.is_file():
            continue

        candidates.append(path)

    def score(path: Path) -> tuple[int, str]:
        relative = path.relative_to(tool_dir)
        name = path.name.lower()
        depth = len(relative.parts)

        value = 100

        if depth == 1:
            value -= 40

        if name in {"main.py", "__main__.py", "cli.py", "app.py", "run.py"}:
            value -= 30

        if name == f"{tool_dir.name.lower()}.py":
            value -= 25

        return value, str(relative)

    return sorted(candidates, key=score)


def choose_entry_file(tool_dir: Path, provided_entry: str | None) -> Path:
    """Choose or prompt for the entry file."""
    if provided_entry:
        raw_entry = Path(provided_entry).expanduser()

        if raw_entry.is_absolute():
            entry = raw_entry.resolve()
        else:
            entry = (tool_dir / raw_entry).resolve()
    else:
        candidates = find_python_entry_candidates(tool_dir)

        if not candidates:
            raise FileNotFoundError("No Python files found in the selected directory.")

        print("")
        print("Likely Python entry files:")
        for index, candidate in enumerate(candidates[:20], start=1):
            print(f"{index}) {candidate.relative_to(tool_dir)}")

        while True:
            answer = input("\nSelect entry file number or enter a relative path: ").strip()

            if answer.isdigit():
                index = int(answer)
                if 1 <= index <= min(len(candidates), 20):
                    entry = candidates[index - 1].resolve()
                    break

            entry = (tool_dir / answer).resolve()
            break

    if not entry.is_file():
        raise FileNotFoundError(f"Entry file does not exist: {entry}")

    if not is_relative_to(entry, tool_dir):
        raise ValueError("Entry file must be inside the selected tool directory.")

    return entry


def get_command_name(provided_name: str | None) -> str:
    """Get and validate command name."""
    while True:
        name = provided_name or input("\nCommand name to create: ").strip()
        ok, message = validate_command_name(name)

        if ok:
            return name

        print(f"Invalid command name: {message}")

        if provided_name:
            raise ValueError(message)


def resolve_install_plan(args: Namespace) -> tuple[Path, str]:
    """Resolve install directory and installation scope."""
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


def describe_scope(scope: str) -> tuple[str, str]:
    """Return availability and execution notes for a scope."""
    if scope == "system":
        return (
            "all users with /usr/local/bin in PATH",
            "invoking user, not root unless executed with sudo",
        )

    if scope == "custom":
        return (
            "users who have the custom install directory in PATH",
            "invoking user, not root unless executed with sudo",
        )

    return (
        "current user only",
        "current user, not root unless executed with sudo",
    )


def should_create_venv(args: Namespace) -> bool:
    if getattr(args, "no_venv", False):
        return False

    if getattr(args, "venv", False):
        return True

    return confirm(
        "Create .venv inside the selected tool directory?",
        default=True,
        assume_yes=args.yes,
    )


def should_install_dependencies(
    args: Namespace,
    dependency_files: list[Path],
    create_venv_selected: bool,
) -> bool:
    if not dependency_files:
        return False

    if not create_venv_selected:
        print("")
        print("Dependency installation is skipped because no virtual environment was selected.")
        print("CmdForge will not install dependencies into the system Python.")
        return False

    if getattr(args, "install_deps", False):
        return True

    if getattr(args, "no_install_deps", False):
        return False

    print("")
    print("Security warning:")
    print("Installing dependencies from unknown repositories can run untrusted code.")
    print("Review dependency files before continuing.")

    return confirm(
        "Install supported dependencies into .venv?",
        default=False,
        assume_yes=args.yes,
    )


def run_command_builder(args: Namespace | None = None) -> int:
    if args is None:
        args = Namespace(
            path=None,
            entry=None,
            name=None,
            install_dir=None,
            system=False,
            scope=None,
            venv=False,
            no_venv=False,
            install_deps=False,
            no_install_deps=False,
            yes=False,
            dry_run=False,
        )

    print_section("CmdForge commandify")

    print("Security reminder:")
    print("Only wrap and run tools you trust or have reviewed.")
    print("Avoid running unknown tools with sudo.")

    tool_dir_input = args.path or input("\nPython tool directory: ").strip()
    tool_dir = expand_path(tool_dir_input)

    if not tool_dir.is_dir():
        raise NotADirectoryError(f"Tool directory does not exist: {tool_dir}")

    entry_file = choose_entry_file(tool_dir, args.entry)
    command_name = get_command_name(args.name)
    install_dir, scope = resolve_install_plan(args)
    availability, execution_note = describe_scope(scope)

    create_venv_selected = should_create_venv(args)
    dependency_files = find_dependency_files(tool_dir)

    print_section("Dependency detection")
    describe_dependency_files(dependency_files)

    install_deps_selected = should_install_dependencies(
        args,
        dependency_files,
        create_venv_selected,
    )

    existing_command = command_exists_in_path(command_name)
    if existing_command:
        print("")
        print(f"Existing command found in PATH: {existing_command}")

    target_command = install_dir / command_name
    overwrite = False

    if target_command.exists():
        overwrite = confirm(
            f"Target command already exists at {target_command}. Back it up and overwrite?",
            default=False,
            assume_yes=args.yes,
        )
        if not overwrite:
            print("Aborted: target command already exists.")
            return 1

    python_executable = venv_python_path(tool_dir) if create_venv_selected else None

    print_section("Planned action")
    print(f"Tool directory:      {tool_dir}")
    print(f"Entry file:          {entry_file}")
    print(f"Command name:        {command_name}")
    print(f"Scope:               {scope}")
    print(f"Available to:        {availability}")
    print(f"Runs as:             {execution_note}")
    print(f"Install directory:   {install_dir}")
    print(f"Target command:      {target_command}")
    print(f"Use virtualenv:      {'yes' if create_venv_selected else 'no'}")
    print(f"Install deps:        {'yes' if install_deps_selected else 'no'}")
    print(f"Dry-run:             {'yes' if args.dry_run else 'no'}")

    if scope == "system":
        print("")
        print("System scope note:")
        print("/usr/local/bin is usually writable only by root.")
        print("CmdForge will not automatically use sudo.")

    if args.dry_run:
        create_wrapper(
            command_name=command_name,
            entry_file=entry_file,
            install_dir=install_dir,
            python_executable=python_executable,
            overwrite=overwrite,
            dry_run=True,
            scope=scope,
        )
        print("")
        print("Dry-run complete. No files were changed.")
        return 0

    if not confirm("\nCreate this command wrapper?", default=False, assume_yes=args.yes):
        print("Aborted.")
        return 1

    actual_python_executable = None
    created_or_used_venv = None

    if create_venv_selected:
        actual_python_executable = create_venv(tool_dir)
        created_or_used_venv = venv_path_for(tool_dir)

    if install_deps_selected and actual_python_executable is not None:
        install_dependencies(actual_python_executable, dependency_files)

    try:
        command_path = create_wrapper(
            command_name=command_name,
            entry_file=entry_file,
            install_dir=install_dir,
            python_executable=actual_python_executable,
            overwrite=overwrite,
            dry_run=False,
            scope=scope,
        )
    except PermissionError as exc:
        print("")
        print(f"Permission error: {exc}")
        print("If you selected system scope, rerun with appropriate privileges or use --scope user.")
        return 1

    print_section("Done")
    print(f"Command created: {command_path}")
    print(f"Test it with: {command_name} --help")

    print_path_hint(install_dir)
    print_rollback(command_path, created_or_used_venv)

    return 0
