# Changelog

All notable changes to CmdForge will be documented in this file.

## v0.1.1-alpha - 2026-05-17

### Added

- Added install scope support for generated commands.
- Added `--scope user` for current-user command installation.
- Added `--scope system` for system-wide command installation.
- Kept `--system` as an alias for system scope.
- Added `cmdforge remove` for removing CmdForge-managed wrappers.
- Added wrapper metadata markers for safer removal.
- Added tests for command removal and wrapper metadata.
- Added `.deb` package build path to roadmap.

### Security

- Clarified that generated commands run as the invoking user, not automatically as root.
- CmdForge still avoids automatic `sudo` usage.
- `cmdforge remove` refuses to remove non-CmdForge files unless `--force` is used.

## v0.1.0-alpha - 2026-05-17

Initial alpha release.

### Added

- Added CmdForge Python package structure.
- Added `cmdforge` CLI entry point.
- Added `cmdforge commandify` workflow.
- Added interactive menu mode.
- Added non-interactive commandify flags:
  - `--path`
  - `--entry`
  - `--name`
  - `--install-dir`
  - `--system`
  - `--venv`
  - `--no-venv`
  - `--install-deps`
  - `--no-install-deps`
  - `--dry-run`
  - `--yes`
- Added safe command-name validation.
- Added Python entry-file detection.
- Added dependency file detection.
- Added support for installing `requirements*.txt` files into tool-specific `.venv`.
- Added safe Bash wrapper generation.
- Added argument forwarding with `"$@"`.
- Added default user-level install path: `~/.local/bin`.
- Added rollback instructions after wrapper creation.
- Added `cmdforge --version`.
- Added user-level install script: `scripts/install-user.sh`.
- Added user-level uninstall script: `scripts/uninstall-user.sh`.
- Added placeholder module for future Python 2 to Python 3 helper.
- Added initial unit tests.
- Added public-facing README with install and usage documentation.

### Security

- Avoids installing dependencies into system Python.
- Uses user-level install path by default.
- Supports dry-run before creating wrappers.
- Warns before dependency installation.
- Validates command names.
- Avoids hard-coded target tool paths.
- Preserves wrapper arguments safely using `"$@"`.

### Notes

This is an alpha release. The command-builder workflow is functional, but the project is still under active development.
