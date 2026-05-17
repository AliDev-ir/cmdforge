"""Main CLI entry point for CmdForge."""

from __future__ import annotations

import argparse

from cmdforge import __version__
from cmdforge.command_builder import run_command_builder
from cmdforge.command_remover import run_command_remover
from cmdforge.py2to3_converter import run_py2to3, run_py2to3_placeholder


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cmdforge",
        description="Safely turn Python tools into permanent Linux commands.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")

    commandify = subparsers.add_parser(
        "commandify",
        help="Create a permanent Linux command from a Python tool.",
    )
    commandify.add_argument("--path", help="Path to the Python tool directory.")
    commandify.add_argument("--entry", help="Entry Python file, absolute or relative to --path.")
    commandify.add_argument("--name", help="Command name to create.")
    commandify.add_argument(
        "--install-dir",
        help="Directory where the wrapper command should be created. Default: ~/.local/bin",
    )
    commandify.add_argument(
        "--scope",
        choices=["user", "system"],
        default=None,
        help="Installation scope. Default: user.",
    )
    commandify.add_argument(
        "--system",
        action="store_true",
        help="Alias for --scope system. Installs into /usr/local/bin.",
    )
    commandify.add_argument(
        "--venv",
        action="store_true",
        help="Create or reuse .venv inside the selected tool directory.",
    )
    commandify.add_argument(
        "--no-venv",
        action="store_true",
        help="Do not create a virtual environment.",
    )
    commandify.add_argument(
        "--install-deps",
        action="store_true",
        help="Install supported dependency files into .venv.",
    )
    commandify.add_argument(
        "--no-install-deps",
        action="store_true",
        help="Do not install dependencies.",
    )
    commandify.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Automatically confirm prompts where possible.",
    )
    commandify.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned changes without creating files.",
    )

    remove = subparsers.add_parser(
        "remove",
        help="Remove a CmdForge-managed command wrapper.",
    )
    remove.add_argument("name", help="Command name to remove.")
    remove.add_argument(
        "--install-dir",
        help="Directory where the wrapper command exists. Default: ~/.local/bin",
    )
    remove.add_argument(
        "--scope",
        choices=["user", "system"],
        default=None,
        help="Removal scope. Default: user.",
    )
    remove.add_argument(
        "--system",
        action="store_true",
        help="Alias for --scope system. Removes from /usr/local/bin.",
    )
    remove.add_argument(
        "--remove-venv",
        action="store_true",
        help="Also remove the detected tool .venv if possible.",
    )
    remove.add_argument(
        "--force",
        action="store_true",
        help="Remove even if the wrapper is not marked as managed by CmdForge.",
    )
    remove.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Automatically confirm prompts where possible.",
    )

    py2to3 = subparsers.add_parser(
        "py2to3",
        help="Safely scan or convert Python 2 code to Python 3.",
    )
    py2to3.add_argument("--path", help="Python file or project directory to scan or convert.")
    py2to3.add_argument("--output", help="Output file or directory for converted copy.")
    py2to3.add_argument("--report", help="Write a JSON report to this path.")
    py2to3.add_argument(
        "--dry-run",
        action="store_true",
        help="Scan only and do not create or modify files.",
    )
    py2to3.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Automatically confirm prompts where possible.",
    )

    return parser


def run_interactive_menu() -> int:
    print("CmdForge")
    print("========")
    print("1) Create a Linux command from a Python tool")
    print("2) Remove a CmdForge-managed command")
    print("3) Python 2 to Python 3 helper")
    print("q) Quit")

    choice = input("\nSelect an option: ").strip().lower()

    if choice == "1":
        return run_command_builder()

    if choice == "2":
        name = input("\nCommand name to remove: ").strip()
        args = argparse.Namespace(
            name=name,
            install_dir=None,
            scope=None,
            system=False,
            remove_venv=False,
            force=False,
            yes=False,
        )
        return run_command_remover(args)

    if choice == "3":
        return run_py2to3_placeholder()

    if choice in {"q", "quit", "exit"}:
        print("Bye.")
        return 0

    print("Invalid option.")
    return 2


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "commandify":
            return run_command_builder(args)

        if args.command == "remove":
            return run_command_remover(args)

        if args.command == "py2to3":
            if not getattr(args, "path", None):
                return run_py2to3_placeholder()
            return run_py2to3(args)

        return run_interactive_menu()
    except KeyboardInterrupt:
        print("\nAborted.")
        return 130
    except Exception as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
