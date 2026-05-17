# Changelog

All notable changes to CmdForge will be documented in this file.

## v1.0.0-rc1 - 2026-05-17

### Release Candidate

- Promoted CmdForge from beta toward the first stable release candidate.
- Updated Python package version to `1.0.0rc1`.
- Updated Debian package version mapping to `1.0.0~rc1`.
- Kept the CLI feature set frozen for stable release validation.
- Continued using the self-contained Debian package model under `/opt/cmdforge`.

### Stability

- Maintains command builder, wrapper removal, py2to3 helper, and Debian packaging workflows.
- Uses the existing release checklist and Debian smoke test process.
- No new runtime feature was added in this release candidate.

### Notes

- This release candidate should be validated with the full release checklist before `v1.0.0`.
- If no blockers are found, the next stable target is `v1.0.0`.

## v0.3.1-beta - 2026-05-17

### Changed

- Improved Debian maintainer scripts for upgrade-aware behavior.
- Updated `postinst` to reinstall CmdForge into the package virtual environment during configure.
- Updated `prerm` to preserve `/opt/cmdforge/.venv` during package upgrades.
- Added `postrm` handling for purge cleanup.
- Added Debian package smoke test script.
- Added release checklist documentation.

### Tested

- Tested install of `0.3.0~beta1`.
- Tested upgrade from `0.3.0~beta1` to `0.3.1~beta1`.
- Verified `/usr/bin/cmdforge --version` reports the upgraded version.
- Verified package removal cleans `/usr/bin/cmdforge`.
- Verified package removal cleans `/opt/cmdforge/.venv`.

### Notes

- After `dpkg -r`, Debian may keep package state as `rc`.
- Use `sudo dpkg -P cmdforge` to purge remaining package state.

## v0.3.0-beta - 2026-05-17

### Added

- Added `scripts/build-deb.sh`.
- Added self-contained Debian package build path.
- Added offline wheelhouse packaging for CmdForge dependencies.
- Added Debian package install wrapper at `/usr/bin/cmdforge`.
- Added package runtime location under `/opt/cmdforge`.
- Added `.gitignore` rules for build artifacts and local conversion outputs.

### Packaging

- The `.deb` package installs CmdForge into a dedicated virtual environment under `/opt/cmdforge/.venv`.
- The package installs from local wheels and does not require internet access during installation.
- The package avoids installing Python dependencies into the system Python.

### Notes

- This is the first beta release with Debian package support.
- The package install/remove workflow has been smoke-tested on Kali.
- Upgrade behavior still needs additional testing before declaring stable.

## v0.2.1-alpha - 2026-05-17

### Added

- Added `--report` option to `cmdforge py2to3`.
- Added JSON report output for dry-run and conversion workflows.
- Added finding summaries to py2to3 scan output.
- Added syntax check result reporting.
- Added tests for syntax check behavior.

### Changed

- Replaced compileall-based output validation with direct syntax checks.
- Avoided generating `__pycache__` during py2to3 syntax checks.
- Improved py2to3 terminal output with summary counts.

### Notes

- The py2to3 workflow still avoids in-place conversion.
- Runtime correctness still requires manual review after conversion.

## v0.2.0-alpha - 2026-05-17

### Added

- Added `cmdforge py2to3`.
- Added Python 2 pattern scanner.
- Added safe dry-run scan mode for Python 2 projects.
- Added converted-copy workflow using an output path.
- Added project copy logic that ignores `.git`, `.venv`, cache directories, build directories, and bytecode files.
- Added conversion engine integration using `fissix`.
- Added compile check after conversion.
- Added unit tests for py2to3 scanning and copy behavior.

### Security

- The original Python 2 project is not modified.
- Conversion runs on a copied output directory.
- Existing output directories are not overwritten.
- In-place conversion is intentionally not included yet.

### Notes

- Python 2 to Python 3 conversion may still require manual review.
- Passing compile checks does not guarantee runtime correctness.

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
