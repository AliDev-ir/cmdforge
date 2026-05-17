# CmdForge

CmdForge is a Linux-focused Python CLI tool that helps you safely turn Python tools into permanent terminal commands.

It is designed for developers, Linux users, security researchers, and tool collectors who often download Python tools from GitHub and want to run them from anywhere in the terminal.

Instead of running:

    python3 /path/to/tool/main.py

you can create a command like:

    mytool

## Status

Current version: `0.1.0`

CmdForge is in early development. The initial `commandify` workflow is implemented and tested locally. The Python 2 to Python 3 helper is planned as a future module.

## Why CmdForge?

Many Python tools downloaded from GitHub are not packaged as proper Linux commands. Users often create manual wrapper scripts in `/usr/local/bin` or `~/.local/bin`.

CmdForge automates this workflow while keeping safety, reversibility, and clarity in mind.

## Features

- Interactive CLI workflow
- Subcommand-based usage
- Python tool directory validation
- Python entry-file selection
- Safe command-name validation
- Optional `.venv` creation inside the target tool directory
- Dependency file detection
- Optional dependency installation into `.venv`
- User-level command installation in `~/.local/bin`
- Optional custom install directory
- Dry-run mode
- Existing command detection
- Safe Bash wrapper generation
- Argument forwarding with `"$@"`
- Rollback instructions
- Initial unit tests

## Planned Features

- Improved dependency handling for `pyproject.toml`, `setup.py`, `Pipfile`, and Poetry projects
- Better interactive entry-file selection
- Optional system-wide installation helper for `/usr/local/bin`
- Wrapper removal command
- Command listing
- Update/rebuild existing wrappers
- Python 2 to Python 3 migration helper
- More automated tests
- PyPI packaging

## Installation for Development

Clone the repository:

    git clone https://github.com/AliDev-ir/cmdforge.git
    cd cmdforge

Create and activate a virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

Install CmdForge in editable mode:

    python -m pip install --upgrade pip
    python -m pip install -e .

Check the CLI:

    cmdforge --help
    cmdforge --version

## Usage

Run interactive mode:

    cmdforge

Create a command from a Python tool:

    cmdforge commandify

Use non-interactive mode:

    cmdforge commandify --path /path/to/python/tool --entry main.py --name mytool

Create or reuse `.venv` inside the tool directory:

    cmdforge commandify --path /path/to/python/tool --entry main.py --name mytool --venv

Preview changes without writing files:

    cmdforge commandify --path /path/to/python/tool --entry main.py --name mytool --venv --dry-run

Skip dependency installation:

    cmdforge commandify --path /path/to/python/tool --entry main.py --name mytool --venv --no-install-deps

Install supported dependency files into `.venv`:

    cmdforge commandify --path /path/to/python/tool --entry main.py --name mytool --venv --install-deps

Use a custom install directory:

    cmdforge commandify --path /path/to/python/tool --entry main.py --name mytool --install-dir ~/.local/bin

## Default Install Location

CmdForge installs wrapper commands into:

    ~/.local/bin

This avoids requiring `sudo` and is safer than writing to system-wide locations by default.

Make sure `~/.local/bin` is in your `PATH`:

    export PATH="$HOME/.local/bin:$PATH"

You can add that line to your shell configuration file, such as:

    ~/.bashrc
    ~/.zshrc

## Wrapper Example

If a virtual environment is used, CmdForge creates a wrapper like:

    #!/usr/bin/env bash
    exec /path/to/tool/.venv/bin/python /path/to/tool/main.py "$@"

Without a virtual environment, the wrapper uses:

    #!/usr/bin/env bash
    exec /usr/bin/env python3 /path/to/tool/main.py "$@"

## Dependency Detection

CmdForge currently detects common dependency files such as:

- `requirements.txt`
- `requirements-dev.txt`
- `requirements.clean.txt`
- `pyproject.toml`
- `setup.py`
- `setup.cfg`
- `Pipfile`
- `Pipfile.lock`
- `poetry.lock`

In version `0.1.0`, automatic installation is limited to `requirements*.txt` files.

Other files may be detected but are not installed automatically yet.

## Security Notes

CmdForge may work with tools downloaded from GitHub or other third-party sources. It does not make unknown code safe.

Before creating wrappers or installing dependencies:

- Review the source code.
- Review dependency files.
- Avoid running unknown tools with elevated privileges.
- Do not expose secrets, tokens, cookies, or credentials.
- Prefer user-level installation over system-wide installation.
- Use `--dry-run` before creating commands.
- Only use security tools in environments where you have authorization.

CmdForge avoids installing dependencies into the system Python. Dependency installation is intended to happen inside a tool-specific `.venv`.

## Rollback

CmdForge prints rollback instructions after creating a command.

Typical rollback:

    rm -f ~/.local/bin/mytool
    rm -rf /path/to/tool/.venv

## Development

Run syntax checks:

    python -m compileall src tests

Run tests:

    python -m unittest discover -s tests -v

## Current Architecture

    cmdforge/
    ├── README.md
    ├── LICENSE
    ├── pyproject.toml
    ├── src/
    │   └── cmdforge/
    │       ├── __init__.py
    │       ├── cli.py
    │       ├── command_builder.py
    │       ├── dependency_detector.py
    │       ├── dependency_installer.py
    │       ├── py2to3_converter.py
    │       ├── utils.py
    │       ├── venv_manager.py
    │       └── wrapper_manager.py
    └── tests/

## License

MIT
