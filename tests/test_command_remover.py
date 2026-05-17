import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

from cmdforge.command_remover import run_command_remover
from cmdforge.wrapper_manager import create_wrapper, is_cmdforge_wrapper, read_wrapper_metadata


class TestCommandRemover(unittest.TestCase):
    def test_remove_cmdforge_managed_wrapper(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            install_dir = Path(temp_dir)

            target = create_wrapper(
                command_name="sample-tool",
                entry_file=Path("/tmp/tool/main.py"),
                install_dir=install_dir,
                python_executable=None,
                overwrite=False,
                dry_run=False,
                scope="user",
            )

            self.assertTrue(target.exists())
            self.assertTrue(is_cmdforge_wrapper(target))

            args = Namespace(
                name="sample-tool",
                install_dir=str(install_dir),
                scope=None,
                system=False,
                remove_venv=False,
                force=False,
                yes=True,
            )

            result = run_command_remover(args)

            self.assertEqual(result, 0)
            self.assertFalse(target.exists())

    def test_wrapper_metadata_is_written(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            install_dir = Path(temp_dir)

            target = create_wrapper(
                command_name="sample-tool",
                entry_file=Path("/tmp/tool/main.py"),
                install_dir=install_dir,
                python_executable=Path("/tmp/tool/.venv/bin/python"),
                overwrite=False,
                dry_run=False,
                scope="user",
            )

            metadata = read_wrapper_metadata(target)

            self.assertEqual(metadata["Command name"], "sample-tool")
            self.assertEqual(metadata["Scope"], "user")
            self.assertEqual(metadata["Entry file"], "/tmp/tool/main.py")
            self.assertEqual(metadata["Python executable"], "/tmp/tool/.venv/bin/python")


if __name__ == "__main__":
    unittest.main()
