#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
    cat <<'EOF'
CmdForge user installer

Usage:
  scripts/install-user.sh [options]

Options:
  --editable           Install CmdForge in editable mode for development.
  --force              Overwrite an existing ~/.local/bin/cmdforge wrapper.
  --install-dir DIR    Install wrapper into DIR. Default: ~/.local/bin
  --python PYTHON      Python interpreter to use. Default: python3
  -h, --help           Show this help message.

This installer does not use sudo.
It installs the cmdforge wrapper at user level by default.
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd -P)"

PYTHON_BIN="${PYTHON:-python3}"
INSTALL_DIR="${HOME}/.local/bin"
VENV_DIR="${PROJECT_ROOT}/.venv"
EDITABLE=0
FORCE=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --editable)
            EDITABLE=1
            shift
            ;;
        --force)
            FORCE=1
            shift
            ;;
        --install-dir)
            if [[ $# -lt 2 ]]; then
                echo "Error: --install-dir requires a value." >&2
                exit 2
            fi
            INSTALL_DIR="$2"
            shift 2
            ;;
        --python)
            if [[ $# -lt 2 ]]; then
                echo "Error: --python requires a value." >&2
                exit 2
            fi
            PYTHON_BIN="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Error: unknown option: $1" >&2
            usage
            exit 2
            ;;
    esac
done

case "${INSTALL_DIR}" in
    "~/"*) INSTALL_DIR="${HOME}/${INSTALL_DIR#~/}" ;;
esac

if [[ ! -f "${PROJECT_ROOT}/pyproject.toml" ]]; then
    echo "Error: pyproject.toml not found. Run this script from the CmdForge repository." >&2
    exit 1
fi

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
    echo "Error: Python interpreter not found: ${PYTHON_BIN}" >&2
    exit 1
fi

mkdir -p "${INSTALL_DIR}"
INSTALL_DIR="$(cd "${INSTALL_DIR}" && pwd -P)"

TARGET="${INSTALL_DIR}/cmdforge"
VENV_PYTHON="${VENV_DIR}/bin/python"
VENV_CMD="${VENV_DIR}/bin/cmdforge"

echo "CmdForge installer"
echo "=================="
echo "Project root:      ${PROJECT_ROOT}"
echo "Python:            ${PYTHON_BIN}"
echo "Virtualenv:        ${VENV_DIR}"
echo "Install directory: ${INSTALL_DIR}"
echo "Target command:    ${TARGET}"
echo "Editable install:  $([[ ${EDITABLE} -eq 1 ]] && echo yes || echo no)"
echo ""

if [[ -e "${TARGET}" ]]; then
    if [[ ${FORCE} -ne 1 ]] && ! grep -q "Managed by CmdForge installer" "${TARGET}" 2>/dev/null; then
        echo "Error: target already exists and is not managed by CmdForge:" >&2
        echo "  ${TARGET}" >&2
        echo "Use --force to overwrite it." >&2
        exit 1
    fi
fi

echo "Creating or reusing virtual environment..."
"${PYTHON_BIN}" -m venv "${VENV_DIR}"

echo "Upgrading pip..."
"${VENV_PYTHON}" -m pip install --upgrade pip

if [[ ${EDITABLE} -eq 1 ]]; then
    echo "Installing CmdForge in editable mode..."
    "${VENV_PYTHON}" -m pip install -e "${PROJECT_ROOT}"
else
    echo "Installing CmdForge..."
    "${VENV_PYTHON}" -m pip install "${PROJECT_ROOT}"
fi

if [[ ! -x "${VENV_CMD}" ]]; then
    echo "Error: installed cmdforge executable not found: ${VENV_CMD}" >&2
    exit 1
fi

quoted_cmd="$(printf '%q' "${VENV_CMD}")"
tmp_target="$(mktemp "${TARGET}.tmp.XXXXXX")"

{
    echo '#!/usr/bin/env bash'
    echo '# Managed by CmdForge installer.'
    echo "# Project root: ${PROJECT_ROOT}"
    echo "exec ${quoted_cmd} \"\$@\""
} > "${tmp_target}"

chmod 755 "${tmp_target}"
mv "${tmp_target}" "${TARGET}"

echo ""
echo "Testing installed command..."
"${TARGET}" --version

echo ""
echo "Installed successfully:"
echo "  ${TARGET}"

case ":${PATH}:" in
    *":${INSTALL_DIR}:"*)
        echo ""
        echo "PATH check: ${INSTALL_DIR} is already in PATH."
        ;;
    *)
        echo ""
        echo "PATH notice:"
        echo "  ${INSTALL_DIR} is not currently in PATH."
        echo "Add this line to your shell config if needed:"
        echo "  export PATH=\"${INSTALL_DIR}:\$PATH\""
        ;;
esac

echo ""
echo "Try:"
echo "  ${TARGET} --help"
echo "  ${TARGET} commandify --help"
