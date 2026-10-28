"""Check registry availability before any code accesses Dataset or Databook."""

import subprocess
import sys
import unittest


class RegistryImportTests(unittest.TestCase):
    def test_builtin_formats_available_after_import(self):
        imports = (
            'import tablib; from tablib.formats import registry',
            'from tablib.formats import registry',
        )
        for statement in imports:
            with self.subTest(statement=statement):
                result = subprocess.run(
                    [
                        sys.executable, '-c',
                        (
                            f'{statement}\n'
                            'for name in ("csv", "json", "tsv"):\n'
                            '    assert registry.get_format(name).title == name\n'
                        ),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
