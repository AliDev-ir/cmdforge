import tempfile
import unittest
from pathlib import Path

from cmdforge.wrapper_manager import build_wrapper_content, create_wrapper


class TestWrapperManager(unittest.TestCase):
    def test_build_wrapper_with_venv_python(self):
        content = build_wrapper_content(
            python_executable=Path("/tmp/tool/.venv/bin/python"),
            entry_file=Path("/tmp/tool/main.py"),
        )

        self.assertIn("#!/usr/bin/env bash", content)
        self.assertIn("/tmp/tool/.venv/bin/python", content)
        self.assertIn("/tmp/tool/main.py", content)
        self.assertIn('"$@"', content)

    def test_build_wrapper_without_venv_python(self):
        content = build_wrapper_content(
            python_executable=None,
            entry_file=Path("/tmp/tool/main.py"),
        )

        self.assertIn("exec /usr/bin/env python3", content)
        self.assertIn("/tmp/tool/main.py", content)
        self.assertIn('"$@"', content)

    def test_create_wrapper_dry_run_does_not_create_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            install_dir = Path(temp_dir)
            target = create_wrapper(
                command_name="sample-tool",
                entry_file=Path("/tmp/tool/main.py"),
                install_dir=install_dir,
                python_executable=None,
                overwrite=False,
                dry_run=True,
            )

            self.assertEqual(target, install_dir / "sample-tool")
            self.assertFalse(target.exists())

    def test_create_wrapper_creates_executable_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            install_dir = Path(temp_dir)
            target = create_wrapper(
                command_name="sample-tool",
                entry_file=Path("/tmp/tool/main.py"),
                install_dir=install_dir,
                python_executable=None,
                overwrite=False,
                dry_run=False,
            )

            self.assertTrue(target.exists())
            self.assertTrue(target.stat().st_mode & 0o111)
            self.assertIn('"$@"', target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
