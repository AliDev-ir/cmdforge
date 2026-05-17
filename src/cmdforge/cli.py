"""Main CLI entry point for CmdForge."""

from __future__ import annotations

import argparse

from cmdforge import __version__
from cmdforge.command_builder import run_command_builder
from cmdforge.py2to3_converter import run_py2to3_placeholder


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
        "--system",
        action="store_true",
        help="Install command in /usr/local/bin instead of ~/.local/bin.",
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

    subparsers.add_parser(
        "py2to3",
        help="Python 2 to Python 3 migration helper. Planned feature.",
    )

    return parser


def run_interactive_menu() -> int:
    print("CmdForge")
    print("========")
    print("1) Create a Linux command from a Python tool")
    print("2) Python 2 to Python 3 helper")
    print("q) Quit")

    choice = input("\nSelect an option: ").strip().lower()

    if choice == "1":
        return run_command_builder()

    if choice == "2":
        return run_py2to3_placeholder()

    if choice in {"q", "quit", "exit"}:
        print("Bye.")
        return 0

    print("Invalid option.")
    return 2


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "commandify":
        return run_command_builder(args)

    if args.command == "py2to3":
        return run_py2to3_placeholder()

    return run_interactive_menu()


if __name__ == "__main__":
    raise SystemExit(main())
