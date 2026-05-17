#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "${PROJECT_ROOT}"

PYTHON_BIN="${PYTHON:-python3}"
BUILD_DIR="${PROJECT_ROOT}/build"
DIST_DIR="${PROJECT_ROOT}/dist"
WHEELHOUSE="${BUILD_DIR}/wheelhouse"
DEB_ROOT="${BUILD_DIR}/deb-root"

PACKAGE_NAME="cmdforge"
MAINTAINER="AliDev-ir <alivaez909@gmail.com>"
DESCRIPTION="Safely turn Python tools into permanent Linux commands."

VERSION="$("${PYTHON_BIN}" - <<'PY'
from pathlib import Path
import re

text = Path("src/cmdforge/__init__.py").read_text(encoding="utf-8")
match = re.search(r'__version__\s*=\s*"([^"]+)"', text)
if not match:
    raise SystemExit("Could not read __version__")
print(match.group(1))
PY
)"

DEB_VERSION="${DEB_VERSION:-${VERSION}~alpha1}"
DEB_FILE="${DIST_DIR}/${PACKAGE_NAME}_${DEB_VERSION}_all.deb"

echo "CmdForge .deb builder"
echo "====================="
echo "Project root: ${PROJECT_ROOT}"
echo "Python:       ${PYTHON_BIN}"
echo "Version:      ${VERSION}"
echo "Deb version:  ${DEB_VERSION}"
echo "Output:       ${DEB_FILE}"
echo ""

if ! command -v dpkg-deb >/dev/null 2>&1; then
    echo "Error: dpkg-deb is required." >&2
    exit 1
fi

"${PYTHON_BIN}" -m pip show build wheel setuptools >/dev/null

rm -rf "${BUILD_DIR}"
mkdir -p "${WHEELHOUSE}" "${DIST_DIR}"

echo "Building wheels..."
"${PYTHON_BIN}" -m pip wheel . --wheel-dir "${WHEELHOUSE}"

echo "Preparing deb root..."
mkdir -p "${DEB_ROOT}/DEBIAN"
mkdir -p "${DEB_ROOT}/opt/cmdforge/wheelhouse"
mkdir -p "${DEB_ROOT}/usr/bin"

cp "${WHEELHOUSE}"/*.whl "${DEB_ROOT}/opt/cmdforge/wheelhouse/"

cat > "${DEB_ROOT}/usr/bin/cmdforge" <<'EOF'
#!/usr/bin/env bash
exec /opt/cmdforge/.venv/bin/cmdforge "$@"
EOF
chmod 755 "${DEB_ROOT}/usr/bin/cmdforge"

INSTALLED_SIZE="$(du -sk "${DEB_ROOT}" | awk '{print $1}')"

cat > "${DEB_ROOT}/DEBIAN/control" <<EOF
Package: ${PACKAGE_NAME}
Version: ${DEB_VERSION}
Section: utils
Priority: optional
Architecture: all
Maintainer: ${MAINTAINER}
Depends: python3 (>= 3.10), python3-venv
Installed-Size: ${INSTALLED_SIZE}
Description: ${DESCRIPTION}
 CmdForge is a Linux-focused Python CLI tool that helps users safely turn
 Python tools into permanent terminal commands. It can create command wrappers,
 manage tool-specific virtual environments, remove generated wrappers, and
 assist with Python 2 to Python 3 migration workflows.
EOF

cat > "${DEB_ROOT}/DEBIAN/postinst" <<EOF
#!/usr/bin/env bash
set -Eeuo pipefail

PYTHON_BIN="\${PYTHON:-python3}"
VENV_DIR="/opt/cmdforge/.venv"
WHEELHOUSE="/opt/cmdforge/wheelhouse"

echo "Setting up CmdForge virtual environment..."
"\${PYTHON_BIN}" -m venv "\${VENV_DIR}"

echo "Installing CmdForge into /opt/cmdforge/.venv..."
"\${VENV_DIR}/bin/python" -m pip install --no-index --find-links "\${WHEELHOUSE}" "cmdforge==${VERSION}"

echo "CmdForge installed:"
/usr/bin/cmdforge --version || true
EOF
chmod 755 "${DEB_ROOT}/DEBIAN/postinst"

cat > "${DEB_ROOT}/DEBIAN/prerm" <<'EOF'
#!/usr/bin/env bash
set -Eeuo pipefail

if [[ -d /opt/cmdforge/.venv ]]; then
    rm -rf /opt/cmdforge/.venv
fi
EOF
chmod 755 "${DEB_ROOT}/DEBIAN/prerm"

echo "Building deb package..."
dpkg-deb --build --root-owner-group "${DEB_ROOT}" "${DEB_FILE}"

echo ""
echo "Built package:"
echo "  ${DEB_FILE}"
echo ""
echo "Inspect:"
echo "  dpkg-deb --info ${DEB_FILE}"
echo "  dpkg-deb --contents ${DEB_FILE}"
echo ""
echo "Install test:"
echo "  sudo dpkg -i ${DEB_FILE}"
echo "  /usr/bin/cmdforge --version"
