# ⚒️ CmdForge

<p align="center">
  <strong>Turn Python tools into permanent Linux commands — safely, cleanly, and reversibly.</strong>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-%3E%3D3.10-blue">
  <img alt="Platform" src="https://img.shields.io/badge/Platform-Linux-lightgrey">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green">
  <img alt="Status" src="https://img.shields.io/badge/Status-Alpha-orange">
</p>

---

## 🚀 What is CmdForge?

**CmdForge** is a Linux-focused Python CLI tool that helps you convert Python tools downloaded from GitHub into permanent terminal commands.

Instead of running:

    python3 /path/to/tool/main.py

you can create a clean command like:

    mytool

Then run it from anywhere:

    mytool --help

CmdForge is built for developers, Linux users, security researchers, automation workflows, and anyone who collects or uses Python-based tools.

---

## ✨ Why CmdForge?

Many useful Python tools are not packaged as proper Linux commands.

You often end up manually doing things like:

    sudo nano /usr/local/bin/mytool
    sudo chmod +x /usr/local/bin/mytool

CmdForge automates that workflow while keeping it:

- 🔐 Safer
- 🧹 Cleaner
- 🔁 Reversible
- 🧪 Testable
- 🧰 Suitable for real Linux workflows
- 📦 Ready for open-source distribution

---

## ✅ Current Status

Current version:

    cmdforge 0.3.0

Implemented:

- ✅ `cmdforge` CLI
- ✅ `cmdforge commandify`
- ✅ `cmdforge remove`
- ✅ `cmdforge py2to3`
- ✅ Interactive workflow
- ✅ Non-interactive flags
- ✅ User-level install scope
- ✅ System-wide install scope
- ✅ Safe wrapper generation
- ✅ `.venv` creation for target tools
- ✅ Dependency file detection
- ✅ Optional dependency installation into `.venv`
- ✅ `--dry-run`
- ✅ User-level install scripts
- ✅ Rollback instructions
- ✅ Unit tests
- ✅ Safe Python 2 to Python 3 scan workflow
- ✅ Python 2 to Python 3 converted-copy workflow
- ✅ JSON report output for py2to3
- ✅ Syntax check without generating `__pycache__`
- ✅ Debian `.deb` package builder
- ✅ Self-contained `.deb` package with offline wheelhouse

Planned:

- 🧭 Better interactive UX
- 📦 PyPI / pipx installation
- 📦 Debian `.deb` package build path
- 🧹 Wrapper removal command
- 🔄 Wrapper rebuild/update command
- 🐍 Python 2 to Python 3 migration helper
- 🧪 More tests
- 🧰 Better support for `pyproject.toml`, `setup.py`, Poetry, and Pipenv

---

## 📦 Quick Install

Clone the repository:

    git clone https://github.com/AliDev-ir/cmdforge.git
    cd cmdforge

Install CmdForge as a permanent user-level command:

    scripts/install-user.sh

Check it:

    cmdforge --version
    cmdforge --help

By default, CmdForge installs a wrapper here:

    ~/.local/bin/cmdforge

No `sudo` is required.

---

## 📦 Debian Package

CmdForge can build a self-contained Debian package.

Build the package:

    scripts/build-deb.sh

The package is written to:

    dist/

Example output:

    dist/cmdforge_0.3.0~beta1_all.deb

Install the package:

    sudo dpkg -i dist/cmdforge_*_all.deb

Test the installed command:

    /usr/bin/cmdforge --version
    /usr/bin/cmdforge --help

Remove the package:

    sudo dpkg -r cmdforge

Packaging behavior:

- Installs the runtime wrapper at `/usr/bin/cmdforge`.
- Stores package resources in `/opt/cmdforge`.
- Creates a dedicated virtual environment at `/opt/cmdforge/.venv`.
- Installs CmdForge from local wheels inside `/opt/cmdforge/wheelhouse`.
- Does not install Python dependencies into the system Python.
- Does not require internet access during package installation.

Note:

The first `.deb` packaging path is still beta-level and should be tested on target Debian/Kali systems before relying on it in production.

---

## 🧪 Development Install

For development, use editable mode:

    git clone https://github.com/AliDev-ir/cmdforge.git
    cd cmdforge
    scripts/install-user.sh --editable

Or manually:

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install -e .
    cmdforge --version

---

## 🧰 Basic Usage

Run interactive mode:

    cmdforge

Create a command from a Python tool:

    cmdforge commandify

Use non-interactive mode:

    cmdforge commandify \
      --path /path/to/python/tool \
      --entry main.py \
      --name mytool

Create or reuse `.venv` inside the target tool directory:

    cmdforge commandify \
      --path /path/to/python/tool \
      --entry main.py \
      --name mytool \
      --venv

Preview everything without creating files:

    cmdforge commandify \
      --path /path/to/python/tool \
      --entry main.py \
      --name mytool \
      --venv \
      --dry-run

Install supported dependencies into the tool-specific `.venv`:

    cmdforge commandify \
      --path /path/to/python/tool \
      --entry main.py \
      --name mytool \
      --venv \
      --install-deps

Skip dependency installation:

    cmdforge commandify \
      --path /path/to/python/tool \
      --entry main.py \
      --name mytool \
      --venv \
      --no-install-deps

---

## 👤 User vs System Scope

CmdForge supports install scopes.

User-level scope is the default:

    cmdforge commandify \
      --path /path/to/python/tool \
      --entry main.py \
      --name mytool \
      --scope user

This creates the wrapper in:

    ~/.local/bin

It is intended for the current user only and does not require `sudo`.

System-wide scope:

    cmdforge commandify \
      --path /path/to/python/tool \
      --entry main.py \
      --name mytool \
      --scope system

This uses:

    /usr/local/bin

System-wide commands are available to users who have `/usr/local/bin` in their `PATH`.

Important:

- CmdForge does not automatically use `sudo`.
- A system-wide wrapper may require root permissions to create.
- A command does not automatically run as root.
- A command runs as the user who invokes it.
- It only runs as root if the user explicitly runs it with `sudo`.

The older flag is still supported:

    --system

It acts as an alias for:

    --scope system

---

## 🗑️ Remove Commands

CmdForge can safely remove wrappers that it created.

Remove a user-level command:

    cmdforge remove mytool

Equivalent explicit form:

    cmdforge remove mytool --scope user

Remove a system-wide command:

    cmdforge remove mytool --scope system

CmdForge refuses to remove files that are not marked as CmdForge-managed wrappers unless you use:

    --force

If a wrapper points to a tool-specific `.venv`, CmdForge detects it and tells you. It does not remove the `.venv` unless you request it:

    cmdforge remove mytool --remove-venv

Safety note:

If the wrapper was already removed, CmdForge cannot read its metadata anymore. In that case, remove the tool `.venv` manually if needed:

    rm -rf /path/to/tool/.venv

---

## 🐍 Python 2 to Python 3 Helper

CmdForge includes an early Python 2 to Python 3 helper.

Scan a Python 2 project without changing files:

    cmdforge py2to3 \
      --path /path/to/python2/project \
      --dry-run

Create a converted copy:

    cmdforge py2to3 \
      --path /path/to/python2/project \
      --output /path/to/python2-project-py3

Write a JSON report:

    cmdforge py2to3 \
      --path /path/to/python2/project \
      --dry-run \
      --report /tmp/py2to3-report.json

The original project is not modified.

Current behavior:

- Scans Python files for common Python 2 patterns.
- Ignores `.git`, `.venv`, cache directories, build directories, and bytecode files.
- Copies the project to a separate output path.
- Runs conversion on the copy.
- Runs a Python 3 syntax check on the converted output.
- Writes optional JSON reports with `--report`.
- Avoids creating `__pycache__` during syntax checks.

Important:

- Python 2 to Python 3 conversion is not always fully automatic.
- A successful compile check does not guarantee runtime correctness.
- Some converted files may still require manual review.
- CmdForge does not overwrite the original project.

---

## 🛡️ Safe by Default

CmdForge defaults to user-level installation:

    ~/.local/bin

This is safer than writing to:

    /usr/local/bin

because it does not require `sudo`.

Make sure `~/.local/bin` is in your `PATH`:

    export PATH="$HOME/.local/bin:$PATH"

You can add that line to your shell config, for example:

    ~/.bashrc
    ~/.zshrc

---

## 🧾 Wrapper Example

With virtual environment:

    #!/usr/bin/env bash
    exec /path/to/tool/.venv/bin/python /path/to/tool/main.py "$@"

Without virtual environment:

    #!/usr/bin/env bash
    exec /usr/bin/env python3 /path/to/tool/main.py "$@"

CmdForge preserves command arguments using:

    "$@"

---

## 🔎 Dependency Detection

CmdForge detects common dependency files:

- `requirements.txt`
- `requirements-dev.txt`
- `requirements.clean.txt`
- `pyproject.toml`
- `setup.py`
- `setup.cfg`
- `Pipfile`
- `Pipfile.lock`
- `poetry.lock`

In version `0.3.0`, automatic installation is intentionally limited to:

    requirements*.txt

Other files are detected but not installed automatically yet.

---

## 🔐 Security Notes

CmdForge may work with tools downloaded from GitHub or other third-party sources.

It does **not** make unknown code safe.

Before wrapping or running any tool:

- Review the source code.
- Review dependency files.
- Avoid running unknown tools with `sudo`.
- Do not expose secrets, tokens, cookies, or credentials.
- Prefer `--dry-run` before creating commands.
- Prefer user-level installation.
- Only use security tools in environments where you have authorization.

CmdForge avoids installing dependencies into the system Python. Dependency installation should happen inside a tool-specific `.venv`.

---

## 🧹 Uninstall CmdForge

Remove the user-level CmdForge wrapper:

    scripts/uninstall-user.sh

Remove the wrapper and project `.venv`:

    scripts/uninstall-user.sh --remove-venv

---

## 🔁 Rollback Generated Commands

CmdForge prints rollback instructions after creating a command.

Typical rollback:

    rm -f ~/.local/bin/mytool
    rm -rf /path/to/tool/.venv

---

## 🧪 Run Tests

Compile source and tests:

    python -m compileall src tests

Run unit tests:

    python -m unittest discover -s tests -v

---

## 🧱 Project Structure

    cmdforge/
    ├── README.md
    ├── LICENSE
    ├── pyproject.toml
    ├── scripts/
    │   ├── install-user.sh
    │   └── uninstall-user.sh
    ├── src/
    │   └── cmdforge/
    │       ├── __init__.py
    │       ├── cli.py
    │       ├── command_builder.py
│       ├── command_remover.py
    │       ├── dependency_detector.py
    │       ├── dependency_installer.py
    │       ├── py2to3_converter.py
    │       ├── utils.py
    │       ├── venv_manager.py
    │       └── wrapper_manager.py
    └── tests/

---

## 🗺️ Roadmap

### v0.1.x

- Improve commandify workflow
- Add more tests
- Improve README and examples
- Add safer overwrite handling
- Add wrapper inspection

### v0.2.x

- Add wrapper removal command
- Add wrapper list command
- Improve dependency installation logic
- Support more Python project formats

### Future

- Python 2 to Python 3 migration helper
- PyPI release
- `pipx` install support
- Shell completion
- Richer interactive UI

---

## 📜 License

MIT
