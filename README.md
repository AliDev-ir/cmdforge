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

```bash
python3 /path/to/tool/main.py

you can create a clean command like:

mytool

Then run it from anywhere:

mytool --help

CmdForge is built for developers, Linux users, security researchers, automation workflows, and anyone who collects or uses Python-based tools.

✨ Why CmdForge?

Many useful Python tools are not packaged as proper Linux commands.

You often end up manually doing things like:

sudo nano /usr/local/bin/mytool
sudo chmod +x /usr/local/bin/mytool

CmdForge automates that workflow while keeping it:

🔐 safer
🧹 cleaner
🔁 reversible
🧪 testable
🧰 suitable for real Linux workflows
📦 ready for open-source distribution
✅ Current Status

Current version:

cmdforge 0.1.0

Implemented:

✅ cmdforge CLI
✅ cmdforge commandify
✅ interactive workflow
✅ non-interactive flags
✅ safe wrapper generation
✅ .venv creation for target tools
✅ dependency file detection
✅ optional dependency installation into .venv
✅ --dry-run
✅ user-level install scripts
✅ rollback instructions
✅ unit tests

Planned:

🧭 better interactive UX
📦 PyPI / pipx installation
🧹 wrapper removal command
🔄 wrapper rebuild/update command
🐍 Python 2 to Python 3 migration helper
🧪 more tests
🧰 better support for pyproject.toml, setup.py, Poetry, and Pipenv
📦 Quick Install

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

No sudo is required.

🧪 Development Install

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
🧰 Basic Usage

Run interactive mode:

cmdforge

Create a command from a Python tool:

cmdforge commandify

Use non-interactive mode:

cmdforge commandify \
  --path /path/to/python/tool \
  --entry main.py \
  --name mytool

Create or reuse .venv inside the target tool directory:

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

Install supported dependencies into the tool-specific .venv:

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
🛡️ Safe by Default

CmdForge defaults to user-level installation:

~/.local/bin

This is safer than writing to:

/usr/local/bin

because it does not require sudo.

Make sure ~/.local/bin is in your PATH:

export PATH="$HOME/.local/bin:$PATH"

You can add that line to your shell config, for example:

~/.bashrc
~/.zshrc
🧾 Wrapper Example

With virtual environment:

#!/usr/bin/env bash
exec /path/to/tool/.venv/bin/python /path/to/tool/main.py "$@"

Without virtual environment:

#!/usr/bin/env bash
exec /usr/bin/env python3 /path/to/tool/main.py "$@"

CmdForge preserves command arguments using:

"$@"
🔎 Dependency Detection

CmdForge detects common dependency files:

requirements.txt
requirements-dev.txt
requirements.clean.txt
pyproject.toml
setup.py
setup.cfg
Pipfile
Pipfile.lock
poetry.lock

In version 0.1.0, automatic installation is intentionally limited to:

requirements*.txt

Other files are detected but not installed automatically yet.

🔐 Security Notes

CmdForge may work with tools downloaded from GitHub or other third-party sources.

It does not make unknown code safe.

Before wrapping or running any tool:

Review the source code.
Review dependency files.
Avoid running unknown tools with sudo.
Do not expose secrets, tokens, cookies, or credentials.
Prefer --dry-run before creating commands.
Prefer user-level installation.
Only use security tools in environments where you have authorization.

CmdForge avoids installing dependencies into the system Python. Dependency installation should happen inside a tool-specific .venv.

🧹 Uninstall CmdForge

Remove the user-level CmdForge wrapper:

scripts/uninstall-user.sh

Remove the wrapper and project .venv:

scripts/uninstall-user.sh --remove-venv
🔁 Rollback Generated Commands

CmdForge prints rollback instructions after creating a command.

Typical rollback:

rm -f ~/.local/bin/mytool
rm -rf /path/to/tool/.venv
🧪 Run Tests

Compile source and tests:

python -m compileall src tests

Run unit tests:

python -m unittest discover -s tests -v
🧱 Project Structure
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
│       ├── dependency_detector.py
│       ├── dependency_installer.py
│       ├── py2to3_converter.py
│       ├── utils.py
│       ├── venv_manager.py
│       └── wrapper_manager.py
└── tests/
🗺️ Roadmap
v0.1.x
improve commandify workflow
add more tests
improve README and examples
add safer overwrite handling
add wrapper inspection
v0.2.x
add wrapper removal command
add wrapper list command
improve dependency installation logic
support more Python project formats
Future
Python 2 to Python 3 migration helper
PyPI release
pipx install support
shell completion
richer interactive UI
📜 License

MIT
