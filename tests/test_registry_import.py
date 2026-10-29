"""Exercise registry entry points without first resolving Dataset or Databook."""

import subprocess
import sys
import textwrap
import unittest


class RegistryImportTests(unittest.TestCase):
    def run_in_fresh_process(self, code):
        result = subprocess.run(
            [sys.executable, '-c', textwrap.dedent(code)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_builtin_format_lookup_before_dataset_access(self):
        for statement in (
            'import tablib; from tablib.formats import registry',
            'from tablib.formats import registry',
        ):
            with self.subTest(statement=statement):
                self.run_in_fresh_process(statement + '\n' + textwrap.dedent('''\
                    for name in ('csv', 'json', 'tsv'):
                        assert registry.get_format(name).title == name
                '''))

    def test_builtin_format_iteration_before_dataset_access(self):
        for statement in (
            'import tablib; from tablib.formats import registry',
            'from tablib.formats import registry',
        ):
            with self.subTest(statement=statement):
                self.run_in_fresh_process(statement + '\n' + textwrap.dedent('''\
                    names = {format.title for format in registry.formats()}
                    assert {'csv', 'json', 'tsv'} <= names, names
                '''))

    @unittest.skipUnless(sys.version_info >= (3, 15), 'Requires lazy imports on Python 3.15+')
    def test_import_and_iterator_creation_preserve_lazy_loading(self):
        self.run_in_fresh_process('''\
            import sys
            import tablib
            assert 'tablib.core' not in sys.modules
            from tablib.formats import registry
            formats = registry.formats()
            assert 'tablib.core' not in sys.modules
            assert registry.get_format('csv').title == 'csv'
            assert 'tablib.core' in sys.modules
            for name in ('tablib.formats._xlsx', 'tablib.formats._df', 'tablib.formats._yaml'):
                assert name not in sys.modules, name
        ''')

    def test_custom_registration_is_preserved(self):
        self.run_in_fresh_process('''\
            from tablib.formats import registry
            from tablib.formats._csv import CSVFormat

            class CustomCSV(CSVFormat):
                title = 'custom_csv'

            custom = CustomCSV()
            registry.register('custom_csv', custom)
            assert registry.get_format('custom_csv') is custom
            assert custom in list(registry.formats())
        ''')
