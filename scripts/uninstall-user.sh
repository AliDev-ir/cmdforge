#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
    cat <<'EOF'
CmdForge user uninstaller

Usage:
  scripts/uninstall-user.sh [options]

Options:
  --remove-venv        Also remove the project .venv directory.
  --force              Remove target even if it is not managed by CmdForge installer.
  --install-dir DIR    Wrapper directory. Default: ~/.local/bin
  -h, --help           Show this help message.

This uninstaller does not use sudo.
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd -P)"

INSTALL_DIR="${HOME}/.local/bin"
VENV_DIR="${PROJECT_ROOT}/.venv"
REMOVE_VENV=0
FORCE=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --remove-venv)
            REMOVE_VENV=1
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

mkdir -p "${INSTALL_DIR}"
INSTALL_DIR="$(cd "${INSTALL_DIR}" && pwd -P)"

TARGET="${INSTALL_DIR}/cmdforge"

echo "CmdForge uninstaller"
echo "===================="
echo "Project root:      ${PROJECT_ROOT}"
echo "Install directory: ${INSTALL_DIR}"
echo "Target command:    ${TARGET}"
echo "Remove venv:       $([[ ${REMOVE_VENV} -eq 1 ]] && echo yes || echo no)"
echo ""

if [[ -e "${TARGET}" ]]; then
    if [[ ${FORCE} -ne 1 ]]; then
        if ! grep -q "Managed by CmdForge installer" "${TARGET}" 2>/dev/null; then
            echo "Error: target exists but is not managed by CmdForge installer:" >&2
            echo "  ${TARGET}" >&2
            echo "Use --force to remove it anyway." >&2
            exit 1
        fi

        if ! grep -q "Project root: ${PROJECT_ROOT}" "${TARGET}" 2>/dev/null; then
            echo "Error: target is managed by CmdForge, but for a different project root:" >&2
            echo "  ${TARGET}" >&2
            echo "Use --force to remove it anyway." >&2
            exit 1
        fi
    fi

    rm -f "${TARGET}"
    echo "Removed wrapper:"
    echo "  ${TARGET}"
else
    echo "Wrapper not found; nothing to remove."
fi

if [[ ${REMOVE_VENV} -eq 1 ]]; then
    if [[ "${VIRTUAL_ENV:-}" == "${VENV_DIR}" ]]; then
        echo ""
        echo "Error: refusing to remove the currently active virtual environment." >&2
        echo "Deactivate it first, then run this command again:" >&2
        echo "  deactivate" >&2
        exit 1
    fi

    rm -rf "${VENV_DIR}"
    echo ""
    echo "Removed virtual environment:"
    echo "  ${VENV_DIR}"
fi

echo ""
echo "Uninstall complete."
