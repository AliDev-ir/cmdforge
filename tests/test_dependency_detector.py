import tempfile
import unittest
from pathlib import Path

from cmdforge.dependency_detector import find_dependency_files, supported_install_files


class TestDependencyDetector(unittest.TestCase):
    def test_find_dependency_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tool_dir = Path(temp_dir)

            (tool_dir / "requirements.txt").write_text("requests\n", encoding="utf-8")
            (tool_dir / "requirements-dev.txt").write_text("pytest\n", encoding="utf-8")
            (tool_dir / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
            (tool_dir / "random.txt").write_text("ignored\n", encoding="utf-8")

            found = find_dependency_files(tool_dir)
            found_names = {path.name for path in found}

            self.assertIn("requirements.txt", found_names)
            self.assertIn("requirements-dev.txt", found_names)
            self.assertIn("pyproject.toml", found_names)
            self.assertNotIn("random.txt", found_names)

    def test_supported_install_files_only_requirements_txt(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tool_dir = Path(temp_dir)

            files = [
                tool_dir / "requirements.txt",
                tool_dir / "requirements-dev.txt",
                tool_dir / "pyproject.toml",
                tool_dir / "setup.py",
            ]

            supported = supported_install_files(files)
            supported_names = {path.name for path in supported}

            self.assertIn("requirements.txt", supported_names)
            self.assertIn("requirements-dev.txt", supported_names)
            self.assertNotIn("pyproject.toml", supported_names)
            self.assertNotIn("setup.py", supported_names)


if __name__ == "__main__":
    unittest.main()
