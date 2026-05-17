"""Main CLI entry point for CmdForge."""

from __future__ import annotations

import argparse

from cmdforge.command_builder import run_command_builder
from cmdforge.py2to3_converter import run_py2to3_placeholder


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cmdforge",
        description="Safely turn Python tools into permanent Linux commands.",
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser(
        "commandify",
        help="Create a permanent Linux command from a Python tool.",
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
        return run_command_builder()

    if args.command == "py2to3":
        return run_py2to3_placeholder()

    return run_interactive_menu()


if __name__ == "__main__":
    raise SystemExit(main())
