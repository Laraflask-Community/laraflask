"""
Unit Test: New Artisan Generator Commands
Tests make:request, make:policy, make:resource, make:rule, make:provider,
make:seeder, make:factory, make:observer, make:command — and the new
base classes they depend on (Seeder, Factory, Observer, Model.observe()).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import shutil
import tempfile
import argparse
import unittest
from laraflask.testing.test_case import UnitTestCase
from laraflask.console.artisan import (
    MakeRequestCommand, MakePolicyCommand, MakeResourceCommand, MakeRuleCommand,
    MakeProviderCommand, MakeSeederCommand, MakeFactoryCommand, MakeObserverCommand,
    MakeCommandCommand,
)
from laraflask.orm.seeder import Seeder
from laraflask.orm.factory import Factory
from laraflask.orm.observer import Observer
from laraflask.orm.model import Model
from laraflask.validation.validator import Validator
from laraflask.events.dispatcher import Events, ModelCreated


class GeneratorCommandTestBase(UnitTestCase):
    """
    Runs every generator command test inside a clean temp directory.

    [ID] BUG LAMA yang diperbaiki — dua lapis masalah:
    1. `sys.path` Python selalu memuat entry `''` (string kosong) di
       posisi awal, yang merujuk ke direktori kerja proses SAAT
       INTERPRETER DIMULAI — bukan cwd yang berubah-ubah setelah
       `os.chdir()`.
    2. Yang lebih halus: entry RELATIF lain di `sys.path` (mis.
       `'tests/Unit/../..'`, yang dimasukkan oleh baris
       `sys.path.insert(0, ...)` di awal file test ini) di-cache oleh
       Python sebagai `FileFinder` dengan path ABSOLUT di
       `sys.path_importer_cache` pada saat **pertama kali dipakai** —
       yaitu sebelum `os.chdir()` ke tmp dir terjadi. Setelah cache itu
       terbentuk, `os.chdir()` tidak lagi berpengaruh: Python tetap
       memakai `FileFinder` lama yang menunjuk ke folder project asli.

    Akibatnya, `import_module('app.Requests.X')` di dalam tmp dir tetap
    menemukan package `app` dari project asli, bukan dari tmp dir yang
    baru dibuat — menyebabkan `ModuleNotFoundError` untuk submodule yang
    baru di-generate. Diperbaiki dengan: (a) menghapus seluruh entry
    RELATIF dari `sys.path` (bukan hanya `''`), dan (b) membersihkan
    `sys.path_importer_cache` setiap kali, supaya Python terpaksa
    me-resolve ulang `FileFinder` dari cwd yang benar.

    [EN] OLD BUG fixed here — two layers of the issue:
    1. Python's `sys.path` always contains an `''` (empty string) entry
       at the start, which refers to the process's working directory AT
       INTERPRETER STARTUP — not the cwd as it changes after
       `os.chdir()`.
    2. More subtly: other RELATIVE entries in `sys.path` (e.g.
       `'tests/Unit/../..'`, inserted by this test file's own
       `sys.path.insert(0, ...)` line) get cached by Python as a
       `FileFinder` with an ABSOLUTE path in
       `sys.path_importer_cache` the **first time they're used** — i.e.
       before `os.chdir()` to the temp dir happens. Once that cache
       exists, `os.chdir()` no longer matters: Python keeps using the old
       `FileFinder` pointing at the original project folder.

    As a result, `import_module('app.Requests.X')` inside the temp dir
    still found the `app` package from the original project, instead of
    the freshly-created temp dir — causing a `ModuleNotFoundError` for
    the newly-generated submodule. Fixed by: (a) removing every RELATIVE
    entry from `sys.path` (not just `''`), and (b) clearing
    `sys.path_importer_cache` each time, forcing Python to re-resolve the
    `FileFinder` from the correct cwd.
    """

    def before_each(self):
        self._original_cwd = os.getcwd()
        self._tmp_dir = tempfile.mkdtemp()

        # [ID] Path yang harus disingkirkan mungkin sudah absolut tapi
        # BELUM ter-normalisasi (mis. mengandung literal `..`, seperti
        # `/project/tests/Unit/../..`) — jadi tidak cukup difilter dengan
        # `os.path.isabs()`. Bandingkan versi ter-normalisasi terhadap
        # root project asli.
        # [EN] The path that needs removing may already be absolute but
        # NOT normalized (e.g. contains a literal `..`, like
        # `/project/tests/Unit/../..`) — so filtering with
        # `os.path.isabs()` alone isn't enough. Compare the normalized
        # version against the original project root instead.
        self._removed_path_entries = [
            p for p in sys.path
            if not p or os.path.normpath(p or '.') == os.path.normpath(self._original_cwd)
        ]
        for entry in self._removed_path_entries:
            sys.path.remove(entry)
        sys.path_importer_cache.clear()

        os.chdir(self._tmp_dir)
        self._purge_cached_packages()

    def after_each(self):
        os.chdir(self._original_cwd)
        shutil.rmtree(self._tmp_dir, ignore_errors=True)

        for entry in self._removed_path_entries:
            if entry not in sys.path:
                sys.path.insert(0, entry)
        sys.path_importer_cache.clear()

        self._purge_cached_packages()

    @staticmethod
    def _purge_cached_packages():
        purged = []
        for name in list(sys.modules):
            if name == 'app' or name.startswith('app.') or name == 'database' or name.startswith('database.'):
                del sys.modules[name]
                purged.append(name)
        return purged


class MakeRequestCommandTest(GeneratorCommandTestBase):

    def test_creates_file_at_expected_path(self):
        MakeRequestCommand().handle(argparse.Namespace(name='StorePostRequest'))
        self.assertTrue(os.path.exists('app/Requests/StorePostRequest.py'))

    def test_generated_class_is_importable_and_extends_form_request(self):
        MakeRequestCommand().handle(argparse.Namespace(name='StorePostRequest'))
        sys.path.insert(0, os.getcwd())
        import importlib
        module = importlib.import_module('app.Requests.StorePostRequest')
        from laraflask.validation.validator import FormRequest
        self.assertTrue(issubclass(module.StorePostRequest, FormRequest))
        sys.path.remove(os.getcwd())

    def test_refuses_to_overwrite_existing_file(self):
        MakeRequestCommand().handle(argparse.Namespace(name='StorePostRequest'))
        result = MakeRequestCommand().handle(argparse.Namespace(name='StorePostRequest'))
        self.assertEqual(result, 1)


class MakePolicyCommandTest(GeneratorCommandTestBase):

    def test_creates_file_with_standard_methods(self):
        MakePolicyCommand().handle(argparse.Namespace(name='PostPolicy', model=None))
        with open('app/Policies/PostPolicy.py') as f:
            content = f.read()
        for method in ['view_any', 'view', 'create', 'update', 'delete', 'restore', 'force_delete']:
            self.assertIn(f'def {method}', content)

    def test_model_option_adds_import_and_type_hint(self):
        MakePolicyCommand().handle(argparse.Namespace(name='PostPolicy', model='Post'))
        with open('app/Policies/PostPolicy.py') as f:
            content = f.read()
        self.assertIn('from app.Models.Post import Post', content)
        self.assertIn('model: Post', content)

    def test_generated_policy_extends_base_policy_class(self):
        MakePolicyCommand().handle(argparse.Namespace(name='PostPolicy', model=None))
        sys.path.insert(0, os.getcwd())
        import importlib
        module = importlib.import_module('app.Policies.PostPolicy')
        from laraflask.auth.auth import Policy
        self.assertTrue(issubclass(module.PostPolicy, Policy))
        sys.path.remove(os.getcwd())


class MakeResourceCommandTest(GeneratorCommandTestBase):

    def test_default_uses_api_resource(self):
        MakeResourceCommand().handle(argparse.Namespace(name='PostResource', jsonapi=False))
        with open('app/Resources/PostResource.py') as f:
            content = f.read()
        self.assertIn('from laraflask.api.api import ApiResource', content)

    def test_jsonapi_flag_uses_json_api_resource(self):
        MakeResourceCommand().handle(argparse.Namespace(name='PostResource', jsonapi=True))
        with open('app/Resources/PostResource.py') as f:
            content = f.read()
        self.assertIn('from laraflask.api.jsonapi import JsonApiResource', content)
        self.assertIn("type_ = 'posts'", content)


class MakeRuleCommandTest(GeneratorCommandTestBase):

    def test_creates_rule_registerable_with_validator(self):
        MakeRuleCommand().handle(argparse.Namespace(name='PhoneIdRule'))
        sys.path.insert(0, os.getcwd())
        import importlib
        module = importlib.import_module('app.Rules.PhoneIdRule')
        module.PhoneIdRule.register()

        v = Validator({'phone': 'whatever'}, {'phone': 'required|phone_id_rule'})
        self.assertFalse(v.fails())
        sys.path.remove(os.getcwd())


class MakeProviderCommandTest(GeneratorCommandTestBase):

    def test_generated_provider_extends_service_provider(self):
        MakeProviderCommand().handle(argparse.Namespace(name='PaymentServiceProvider'))
        sys.path.insert(0, os.getcwd())
        import importlib
        module = importlib.import_module('app.Providers.PaymentServiceProvider')
        from laraflask.core.providers import ServiceProvider
        self.assertTrue(issubclass(module.PaymentServiceProvider, ServiceProvider))
        sys.path.remove(os.getcwd())


class MakeSeederCommandTest(GeneratorCommandTestBase):

    def test_generated_seeder_extends_seeder_and_runs(self):
        MakeSeederCommand().handle(argparse.Namespace(name='PostSeeder'))
        sys.path.insert(0, os.getcwd())
        import importlib
        module = importlib.import_module('database.seeders.PostSeeder')
        self.assertTrue(issubclass(module.PostSeeder, Seeder))
        module.PostSeeder().run()  # should not raise (default body is a no-op pass)
        sys.path.remove(os.getcwd())


class MakeFactoryCommandTest(GeneratorCommandTestBase):

    def test_generated_factory_sets_model_attribute(self):
        os.makedirs('app/Models', exist_ok=True)
        with open('app/Models/__init__.py', 'w') as f:
            f.write('')
        with open('app/Models/Post.py', 'w') as f:
            f.write(
                "from laraflask.orm.model import Model\n\n"
                "class Post(Model):\n    __fillable__ = ['title']\n"
            )

        MakeFactoryCommand().handle(argparse.Namespace(name='PostFactory', model='Post'))
        sys.path.insert(0, os.getcwd())
        import importlib
        module = importlib.import_module('database.factories.PostFactory')
        self.assertEqual(module.PostFactory.model.__name__, 'Post')
        sys.path.remove(os.getcwd())


class MakeObserverCommandTest(GeneratorCommandTestBase):

    def test_generated_observer_extends_observer_base(self):
        MakeObserverCommand().handle(argparse.Namespace(name='PostObserver', model=None))
        sys.path.insert(0, os.getcwd())
        import importlib
        module = importlib.import_module('app.Observers.PostObserver')
        self.assertTrue(issubclass(module.PostObserver, Observer))
        sys.path.remove(os.getcwd())

    def test_generated_observer_has_all_lifecycle_hooks(self):
        MakeObserverCommand().handle(argparse.Namespace(name='PostObserver', model=None))
        with open('app/Observers/PostObserver.py') as f:
            content = f.read()
        for hook in ['creating', 'created', 'updating', 'updated', 'deleting', 'deleted', 'saving', 'saved']:
            self.assertIn(f'def {hook}', content)


class MakeCommandCommandTest(GeneratorCommandTestBase):

    def test_generated_command_extends_command_base(self):
        MakeCommandCommand().handle(argparse.Namespace(name='SendDigestCommand', command_name=None))
        sys.path.insert(0, os.getcwd())
        import importlib
        module = importlib.import_module('app.Console.SendDigestCommand')
        from laraflask.console.artisan import Command
        self.assertTrue(issubclass(module.SendDigestCommand, Command))
        sys.path.remove(os.getcwd())

    def test_command_name_auto_derived_when_not_given(self):
        MakeCommandCommand().handle(argparse.Namespace(name='SendDigestCommand', command_name=None))
        with open('app/Console/SendDigestCommand.py') as f:
            content = f.read()
        self.assertIn("name = 'send:digest'", content)

    def test_command_name_explicit_override(self):
        MakeCommandCommand().handle(
            argparse.Namespace(name='SendDigestCommand', command_name='digest:send-now')
        )
        with open('app/Console/SendDigestCommand.py') as f:
            content = f.read()
        self.assertIn("name = 'digest:send-now'", content)


class SeederBaseClassTest(UnitTestCase):

    def test_run_raises_not_implemented_by_default(self):
        with self.assertRaises(NotImplementedError):
            Seeder().run()

    def test_call_runs_other_seeders(self):
        calls = []

        class SeederA(Seeder):
            def run(self):
                calls.append('A')

        class SeederB(Seeder):
            def run(self):
                calls.append('B')

        class MainSeeder(Seeder):
            def run(self):
                self.call(SeederA, SeederB)

        MainSeeder().run()
        self.assertEqual(calls, ['A', 'B'])


class FactoryBaseClassTest(UnitTestCase):

    class DummyModel(Model):
        __table__ = 'dummy'
        __fillable__ = ['name']

    def test_make_without_model_raises(self):
        class NoModelFactory(Factory):
            pass

        with self.assertRaises(NotImplementedError):
            NoModelFactory().make()

    def test_make_returns_single_instance_by_default(self):
        class DummyFactory(Factory):
            model = self.DummyModel
            def definition(self):
                return {'name': 'Test'}

        instance = DummyFactory().make()
        self.assertIsInstance(instance, self.DummyModel)
        self.assertEqual(instance.name, 'Test')

    def test_count_returns_list(self):
        class DummyFactory(Factory):
            model = self.DummyModel
            def definition(self):
                return {'name': 'Test'}

        instances = DummyFactory().count(3).make()
        self.assertEqual(len(instances), 3)

    def test_state_overrides_definition(self):
        class DummyFactory(Factory):
            model = self.DummyModel
            def definition(self):
                return {'name': 'Default'}

        instance = DummyFactory().state(name='Overridden').make()
        self.assertEqual(instance.name, 'Overridden')

    def test_faker_property_works_when_installed(self):
        class DummyFactory(Factory):
            model = self.DummyModel

        try:
            import faker  # noqa
        except ImportError:
            self.skipTest("faker is not installed in this environment")

        fct = DummyFactory()
        self.assertTrue(hasattr(fct.faker, 'name'))


class ModelObserveTest(UnitTestCase):

    class ObservedModel(Model):
        __table__ = 'observed_models'
        __fillable__ = ['title']

    def test_observe_wires_hook_to_matching_model_event(self):
        calls = []

        class TrackingObserver(Observer):
            def created(self, model):
                calls.append(model)

        self.ObservedModel.observe(TrackingObserver)
        instance = self.ObservedModel(title='Hello')
        Events.dispatch(ModelCreated(instance))

        self.assertEqual(len(calls), 1)
        self.assertIs(calls[0], instance)

    def test_observer_does_not_fire_for_other_model_classes(self):
        class OtherModel(Model):
            __table__ = 'other_models'

        calls = []

        class TrackingObserver(Observer):
            def created(self, model):
                calls.append(model)

        self.ObservedModel.observe(TrackingObserver)
        other_instance = OtherModel()
        Events.dispatch(ModelCreated(other_instance))

        self.assertEqual(calls, [])


if __name__ == '__main__':
    unittest.main()
