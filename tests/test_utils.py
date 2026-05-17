import unittest

from cmdforge.utils import validate_command_name


class TestValidateCommandName(unittest.TestCase):
    def test_valid_command_names(self):
        valid_names = [
            "mytool",
            "my-tool",
            "my_tool",
            "my.tool",
            "tool123",
            "123tool",
        ]

        for name in valid_names:
            with self.subTest(name=name):
                ok, message = validate_command_name(name)
                self.assertTrue(ok)
                self.assertEqual(message, "")

    def test_invalid_command_names(self):
        invalid_names = [
            "",
            "/tmp/tool",
            "bad/name",
            "bad name",
            "bad;name",
            ".",
            "..",
        ]

        for name in invalid_names:
            with self.subTest(name=name):
                ok, message = validate_command_name(name)
                self.assertFalse(ok)
                self.assertTrue(message)


if __name__ == "__main__":
    unittest.main()
