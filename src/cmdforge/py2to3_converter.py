"""Safe Python 2 to Python 3 conversion helper for CmdForge."""

from __future__ import annotations

import compileall
import re
import shutil
from argparse import Namespace
from dataclasses import dataclass
from pathlib import Path

from cmdforge.utils import confirm, expand_path, print_section


IGNORED_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
    "build",
    "dist",
}

PY2_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("print statement", re.compile(r"^[ \t]*print [^(#\n]", re.MULTILINE)),
    ("old except syntax", re.compile(r"except\s+[^:\n]+,\s*[^:\n]+:")),
    ("xrange", re.compile(r"\bxrange\s*\(")),
    ("raw_input", re.compile(r"\braw_input\s*\(")),
    ("iteritems", re.compile(r"\.iteritems\s*\(")),
    ("itervalues", re.compile(r"\.itervalues\s*\(")),
    ("iterkeys", re.compile(r"\.iterkeys\s*\(")),
    ("basestring", re.compile(r"\bbasestring\b")),
    ("unicode", re.compile(r"\bunicode\s*\(")),
    ("long", re.compile(r"\blong\s*\(")),
    ("ConfigParser", re.compile(r"\bConfigParser\b")),
    ("SocketServer", re.compile(r"\bSocketServer\b")),
    ("SimpleHTTPServer", re.compile(r"\bSimpleHTTPServer\b")),
    ("urllib2", re.compile(r"\burllib2\b")),
    ("urlparse", re.compile(r"\burlparse\b")),
)


@dataclass(frozen=True)
class Py2Finding:
    path: Path
    kind: str
    count: int


def should_ignore_path(path: Path) -> bool:
    return any(part in IGNORED_DIR_NAMES for part in path.parts)


def iter_python_files(root: Path) -> list[Path]:
    files: list[Path] = []

    if root.is_file():
        if root.suffix == ".py":
            return [root]
        return []

    for path in root.rglob("*.py"):
        if should_ignore_path(path):
            continue
        if path.is_file():
            files.append(path)

    return sorted(files)


def scan_python2_patterns(root: Path) -> list[Py2Finding]:
    findings: list[Py2Finding] = []

    for path in iter_python_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="latin-1")
        except OSError:
            continue

        for label, pattern in PY2_PATTERNS:
            count = len(pattern.findall(text))
            if count:
                findings.append(Py2Finding(path=path, kind=label, count=count))

    return findings


def print_scan_report(root: Path, findings: list[Py2Finding]) -> None:
    print_section("Python 2 scan report")
    print(f"Target path: {root}")
    print(f"Python files scanned: {len(iter_python_files(root))}")

    if not findings:
        print("No obvious Python 2 patterns were detected.")
        return

    print(f"Findings: {len(findings)}")

    current_path: Path | None = None
    shown = 0

    for finding in findings:
        if shown >= 120:
            remaining = len(findings) - shown
            print(f"... {remaining} more findings not shown.")
            break

        if current_path != finding.path:
            current_path = finding.path
            print("")
            print(f"- {finding.path.relative_to(root) if finding.path.is_relative_to(root) else finding.path}")

        print(f"  - {finding.kind}: {finding.count}")
        shown += 1


def copy_project(src: Path, dst: Path) -> None:
    if dst.exists():
        raise FileExistsError(f"Output path already exists: {dst}")

    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return

    def ignore(directory: str, names: list[str]) -> set[str]:
        ignored: set[str] = set()
        for name in names:
            candidate = Path(directory) / name
            if name in IGNORED_DIR_NAMES:
                ignored.add(name)
            elif candidate.suffix in {".pyc", ".pyo"}:
                ignored.add(name)
        return ignored

    shutil.copytree(src, dst, ignore=ignore)


def run_fissix_on_path(target: Path) -> None:
    try:
        from fissix import refactor
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "fissix is required for conversion. Install it with: python -m pip install fissix"
        ) from exc

    files = [str(path) for path in iter_python_files(target)]
    if not files:
        print("No Python files to convert.")
        return

    fixer_names = refactor.get_fixers_from_package("fissix.fixes")
    tool = refactor.RefactoringTool(fixer_names)

    print_section("Converting")
    print(f"Python files to convert: {len(files)}")

    for file_path in files:
        print(f"Converting: {file_path}")
        tool.refactor_file(file_path, write=True)


def compile_output(target: Path) -> bool:
    print_section("Compile check")
    if target.is_file():
        target_dir = target.parent
    else:
        target_dir = target

    ok = compileall.compile_dir(
        str(target_dir),
        quiet=1,
        force=True,
    )

    print(f"Compile result: {'ok' if ok else 'failed'}")
    return bool(ok)


def default_output_path(path: Path) -> Path:
    if path.is_file():
        return path.with_name(path.stem + "-py3" + path.suffix)
    return path.with_name(path.name + "-py3")


def run_py2to3(args: Namespace) -> int:
    print_section("CmdForge py2to3")

    target = expand_path(args.path)

    if not target.exists():
        raise FileNotFoundError(f"Target path does not exist: {target}")

    findings = scan_python2_patterns(target)
    print_scan_report(target, findings)

    if args.dry_run:
        print("")
        print("Dry-run complete. No files were changed.")
        return 0

    output = expand_path(args.output) if args.output else default_output_path(target)

    print_section("Planned action")
    print(f"Source:      {target}")
    print(f"Output:      {output}")
    print("Mode:        copy then convert")
    print("Overwrite:   no")

    if output.exists():
        print("")
        print(f"Output path already exists: {output}")
        print("Choose a different --output path or remove the existing output manually.")
        return 1

    if not confirm("Create converted copy?", default=False, assume_yes=args.yes):
        print("Aborted.")
        return 1

    copy_project(target, output)
    print(f"Copied source to: {output}")

    run_fissix_on_path(output)
    compile_ok = compile_output(output)

    print_section("Done")
    print(f"Converted copy: {output}")

    if not compile_ok:
        print("")
        print("Some files did not compile under Python 3.")
        print("This is expected for many Python 2 projects and requires manual review.")
        return 2

    print("Conversion completed and compile check passed.")
    return 0


def run_py2to3_placeholder() -> int:
    print("Python 2 to Python 3 helper is now available via:")
    print("cmdforge py2to3 --path /path/to/project --dry-run")
    return 0
