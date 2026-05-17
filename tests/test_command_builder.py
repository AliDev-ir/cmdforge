import tempfile
import unittest
from pathlib import Path

from cmdforge.command_builder import find_python_entry_candidates, choose_entry_file


class TestCommandBuilder(unittest.TestCase):
    def test_find_python_entry_candidates_prefers_root_main_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tool_dir = Path(temp_dir)

            main_file = tool_dir / "main.py"
            nested_file = tool_dir / "package" / "worker.py"
            ignored_file = tool_dir / ".venv" / "ignored.py"

            main_file.write_text("print('main')\n", encoding="utf-8")
            nested_file.parent.mkdir()
            nested_file.write_text("print('worker')\n", encoding="utf-8")
            ignored_file.parent.mkdir()
            ignored_file.write_text("print('ignored')\n", encoding="utf-8")

            candidates = find_python_entry_candidates(tool_dir)

            self.assertEqual(candidates[0], main_file)
            self.assertIn(nested_file, candidates)
            self.assertNotIn(ignored_file, candidates)

    def test_choose_entry_file_accepts_relative_entry(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tool_dir = Path(temp_dir)
            entry_file = tool_dir / "tool.py"
            entry_file.write_text("print('tool')\n", encoding="utf-8")

            selected = choose_entry_file(tool_dir, "tool.py")

            self.assertEqual(selected, entry_file.resolve())

    def test_choose_entry_file_rejects_outside_entry(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tool_dir = Path(temp_dir) / "tool"
            outside_dir = Path(temp_dir) / "outside"

            tool_dir.mkdir()
            outside_dir.mkdir()

            outside_file = outside_dir / "outside.py"
            outside_file.write_text("print('outside')\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                choose_entry_file(tool_dir, str(outside_file))


if __name__ == "__main__":
    unittest.main()
