# CmdForge

CmdForge is a Linux-focused Python CLI tool that helps you safely turn Python tools into permanent terminal commands.

Instead of running:

    python3 /path/to/tool/main.py

you can create a command like:

    mytool

## Status

Early development: v0.1.0-alpha

## Main Goal

CmdForge helps automate this workflow:

1. Select a Python tool directory.
2. Detect likely Python entry files.
3. Optionally create a .venv inside the tool directory.
4. Detect dependency files such as requirements.txt, pyproject.toml, setup.py, Pipfile, or poetry.lock.
5. Ask before installing dependencies.
6. Create a safe Linux wrapper command.
7. Install the command in ~/.local/bin by default.
8. Provide rollback instructions.

## Security Notice

CmdForge may work with tools downloaded from GitHub or other sources. It does not make unknown code safe.

Before running wrapped tools or installing their dependencies:

- review the source code,
- review dependency files,
- avoid running unknown tools with elevated privileges,
- do not expose secrets or credentials,
- only use security tools in authorized environments.

## Planned CLI

Interactive mode:

    cmdforge

Command builder:

    cmdforge commandify

Future Python 2 to Python 3 helper:

    cmdforge py2to3

## License

MIT
