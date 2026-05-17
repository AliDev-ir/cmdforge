#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "${PROJECT_ROOT}"

echo "CmdForge .deb smoke test"
echo "========================"
echo "Project root: ${PROJECT_ROOT}"
echo ""

if ! command -v dpkg-deb >/dev/null 2>&1; then
    echo "Error: dpkg-deb is required." >&2
    exit 1
fi

if ! command -v dpkg >/dev/null 2>&1; then
    echo "Error: dpkg is required." >&2
    exit 1
fi

if [[ "${EUID}" -eq 0 ]]; then
    echo "Error: do not run this script as root. It will use sudo only for dpkg steps." >&2
    exit 1
fi

echo "Checking local user-level cmdforge, if present..."
if [[ -x "${HOME}/.local/bin/cmdforge" ]]; then
    echo "User-level cmdforge exists:"
    "${HOME}/.local/bin/cmdforge" --version || true
else
    echo "No user-level cmdforge found at ${HOME}/.local/bin/cmdforge"
fi

echo ""
echo "Building package..."
rm -rf build dist
scripts/build-deb.sh

DEB_FILE="$(find dist -maxdepth 1 -type f -name 'cmdforge_*_all.deb' | sort | tail -1)"

if [[ -z "${DEB_FILE}" ]]; then
    echo "Error: no .deb package found in dist/." >&2
    exit 1
fi

echo ""
echo "Built package: ${DEB_FILE}"

echo ""
echo "Inspecting package metadata..."
dpkg-deb --info "${DEB_FILE}"

echo ""
echo "Inspecting package contents..."
dpkg-deb --contents "${DEB_FILE}" | head -120

echo ""
echo "Installing package..."
sudo dpkg -i "${DEB_FILE}"

echo ""
echo "Testing installed /usr/bin/cmdforge..."
/usr/bin/cmdforge --version
/usr/bin/cmdforge --help >/dev/null
/usr/bin/cmdforge commandify --help >/dev/null
/usr/bin/cmdforge remove --help >/dev/null
/usr/bin/cmdforge py2to3 --help >/dev/null

echo ""
echo "Checking package database..."
dpkg -l | grep '^ii  cmdforge' || {
    echo "Error: cmdforge package not installed according to dpkg." >&2
    exit 1
}

echo ""
echo "Checking PATH conflict behavior..."
echo "PATH cmdforge: $(command -v cmdforge || true)"
echo "System cmdforge: /usr/bin/cmdforge"

if [[ -x "${HOME}/.local/bin/cmdforge" ]]; then
    echo "Notice: user-level cmdforge exists and may shadow /usr/bin/cmdforge depending on PATH order."
    echo "User-level: ${HOME}/.local/bin/cmdforge"
fi

echo ""
echo "Removing package..."
sudo dpkg -r cmdforge

echo ""
echo "Verifying removal..."
test ! -e /usr/bin/cmdforge && echo "/usr/bin/cmdforge removed"
test ! -d /opt/cmdforge/.venv && echo "/opt/cmdforge/.venv removed"

if dpkg -l | grep '^ii  cmdforge' >/dev/null 2>&1; then
    echo "Error: cmdforge still appears installed." >&2
    exit 1
fi

echo ""
echo "Smoke test passed."
