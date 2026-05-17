# CmdForge Release Checklist

## 1. Clean working tree

    git status -sb

Expected:

    ## main...origin/main

## 2. Run source tests

    python -m compileall src tests
    python -m unittest discover -s tests -v

Expected:

    OK

## 3. Check README rendering safety

    grep -n '```' README.md || true

Expected: no output.

## 4. Install editable package locally

    python -m pip install -e .
    cmdforge --version
    cmdforge --help

## 5. Build Debian package

    rm -rf build dist
    scripts/build-deb.sh

Expected artifact:

    dist/cmdforge_<version>~beta1_all.deb

## 6. Inspect Debian package

    dpkg-deb --info dist/cmdforge_*_all.deb
    dpkg-deb --contents dist/cmdforge_*_all.deb | head -120

Verify:

- Package name is `cmdforge`
- Version is correct
- `/usr/bin/cmdforge` exists
- `/opt/cmdforge/wheelhouse/` contains required wheels

## 7. Smoke test Debian package

    scripts/smoke-test-deb.sh

Verify:

- Package installs successfully
- `/usr/bin/cmdforge --version` works
- `commandify`, `remove`, and `py2to3` help pages work
- Package removes successfully
- `/usr/bin/cmdforge` is removed
- `/opt/cmdforge/.venv` is removed

## 8. Upgrade test

Install the previous package, then install the new package over it:

    sudo dpkg -i dist/previous/cmdforge_<old-version>_all.deb
    /usr/bin/cmdforge --version
    sudo dpkg -i dist/cmdforge_<new-version>_all.deb
    /usr/bin/cmdforge --version
    sudo dpkg -r cmdforge

Verify:

- Upgrade succeeds
- New version is reported
- Remove still cleans generated runtime venv

## 9. Tag release

    git tag -a vX.Y.Z-beta -m "Release vX.Y.Z-beta"
    git push origin vX.Y.Z-beta

## 10. GitHub release

Attach:

- `.deb` artifact
- release notes
- install/remove instructions
