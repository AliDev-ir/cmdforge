import tempfile
import unittest
from pathlib import Path

from cmdforge.py2to3_converter import (
    copy_project,
    iter_python_files,
    scan_python2_patterns,
)


class TestPy2To3Converter(unittest.TestCase):
    def test_iter_python_files_ignores_virtualenv_and_cache_dirs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            main_file = root / "main.py"
            ignored_venv_file = root / ".venv" / "ignored.py"
            ignored_cache_file = root / "__pycache__" / "ignored.py"

            main_file.write_text("print 'hello'\n", encoding="utf-8")
            ignored_venv_file.parent.mkdir()
            ignored_venv_file.write_text("print 'ignored'\n", encoding="utf-8")
            ignored_cache_file.parent.mkdir()
            ignored_cache_file.write_text("print 'ignored'\n", encoding="utf-8")

            files = iter_python_files(root)

            self.assertIn(main_file, files)
            self.assertNotIn(ignored_venv_file, files)
            self.assertNotIn(ignored_cache_file, files)

    def test_scan_python2_patterns_detects_common_python2_syntax(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "legacy.py"

            source.write_text(
                "print 'hello'\n"
                "for x in xrange(3):\n"
                "    raw_input('> ')\n"
                "except ValueError, exc:\n"
                "    pass\n",
                encoding="utf-8",
            )

            findings = scan_python2_patterns(root)
            kinds = {finding.kind for finding in findings}

            self.assertIn("print statement", kinds)
            self.assertIn("xrange", kinds)
            self.assertIn("raw_input", kinds)
            self.assertIn("old except syntax", kinds)

    def test_copy_project_ignores_cache_and_virtualenv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source"
            output = root / "output"

            source.mkdir()

            (source / "main.py").write_text("print 'hello'\n", encoding="utf-8")
            (source / ".venv").mkdir()
            (source / ".venv" / "ignored.py").write_text("ignored\n", encoding="utf-8")
            (source / "__pycache__").mkdir()
            (source / "__pycache__" / "ignored.pyc").write_bytes(b"ignored")

            copy_project(source, output)

            self.assertTrue((output / "main.py").exists())
            self.assertFalse((output / ".venv").exists())
            self.assertFalse((output / "__pycache__").exists())


if __name__ == "__main__":
    unittest.main()

from cmdforge.py2to3_converter import syntax_check_output


class TestPy2To3SyntaxCheck(unittest.TestCase):
    def test_syntax_check_does_not_create_pycache(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "main.py"
            source.write_text("print('hello')\n", encoding="utf-8")

            result = syntax_check_output(root)

            self.assertTrue(result.ok)
            self.assertEqual(result.files_checked, 1)
            self.assertFalse((root / "__pycache__").exists())

    def test_syntax_check_reports_syntax_failure(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "broken.py"
            source.write_text("def broken(:\n    pass\n", encoding="utf-8")

            result = syntax_check_output(root)

            self.assertFalse(result.ok)
            self.assertEqual(result.files_checked, 1)
            self.assertEqual(len(result.failures), 1)
            self.assertIn("broken.py", result.failures[0].path)
