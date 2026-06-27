"""
Unit Test: Tinker Command
Tests namespace bootstrapping and model auto-discovery in isolation
(without actually opening an interactive console).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import unittest
from unittest.mock import patch, MagicMock
from laraflask.testing.test_case import UnitTestCase
from laraflask.console.artisan import TinkerCommand


class TinkerNamespaceTest(UnitTestCase):
    """Test that the REPL namespace is built correctly."""

    def before_each(self):
        self.command = TinkerCommand()
        self._original_cwd = os.getcwd()
        # Run from the app/ directory so app.Models is discoverable,
        # mirroring how `python artisan.py tinker` is normally invoked.
        os.chdir(os.path.join(os.path.dirname(__file__), '..', '..'))

    def after_each(self):
        os.chdir(self._original_cwd)

    def test_discover_models_finds_user_model(self):
        models = self.command._discover_models()
        self.assertIn('User', models)

    def test_discovered_model_is_a_model_subclass(self):
        from laraflask.orm.model import Model
        models = self.command._discover_models()
        self.assertTrue(issubclass(models['User'], Model))

    def test_discover_models_skips_dunder_files(self):
        models = self.command._discover_models()
        self.assertNotIn('__init__', models)

    def test_discover_models_returns_empty_dict_when_no_models_dir(self):
        import tempfile
        with tempfile.TemporaryDirectory() as empty_dir:
            os.chdir(empty_dir)
            models = self.command._discover_models()
            self.assertEqual(models, {})

    def test_build_namespace_includes_helpers(self):
        namespace = self.command._build_namespace()
        # Helpers should be present as long as their modules import cleanly.
        self.assertIn('DB', namespace)
        self.assertIn('Hash', namespace)

    def test_build_namespace_includes_discovered_models(self):
        namespace = self.command._build_namespace()
        self.assertIn('User', namespace)


class TinkerIPythonFallbackTest(UnitTestCase):
    """Test that Tinker gracefully falls back when IPython is unavailable."""

    def before_each(self):
        self.command = TinkerCommand()

    def test_try_ipython_returns_false_when_not_installed(self):
        with patch.dict('sys.modules', {'IPython': None}):
            result = self.command._try_ipython({})
            self.assertFalse(result)

    def test_run_stdlib_console_uses_interactive_console(self):
        with patch('code.InteractiveConsole') as mock_console_cls:
            mock_instance = MagicMock()
            mock_console_cls.return_value = mock_instance
            self.command._run_stdlib_console({'foo': 'bar'})
            mock_console_cls.assert_called_once_with(locals={'foo': 'bar'})
            mock_instance.interact.assert_called_once()


if __name__ == '__main__':
    unittest.main()
