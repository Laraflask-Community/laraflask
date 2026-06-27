"""
Unit Test: IoC Container — Contextual Binding & Tagging
Tests advanced container features added on top of the base
singleton/scoped/transient binding system.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import unittest
from laraflask.testing.test_case import UnitTestCase
from laraflask.core.container import Container, BindingResolutionException, ContextualBindingBuilder


# ─── Fixtures ─────────────────────────────────────────────────────────────────

class Logger:
    def log(self, message):
        return f"BASE: {message}"


class FileLogger(Logger):
    def log(self, message):
        return f"FILE: {message}"


class DbLogger(Logger):
    def log(self, message):
        return f"DB: {message}"


class ReportController:
    def __init__(self, logger: Logger):
        self.logger = logger


class UserController:
    def __init__(self, logger: Logger):
        self.logger = logger


class ServiceA:
    def name(self):
        return 'A'


class ServiceB:
    def name(self):
        return 'B'


# ─── Contextual Binding ───────────────────────────────────────────────────────

class ContextualBindingTest(UnitTestCase):

    def before_each(self):
        self.container = Container()

    def test_when_returns_builder(self):
        builder = self.container.when(ReportController)
        self.assertIsInstance(builder, ContextualBindingBuilder)

    def test_different_concretes_get_different_implementations(self):
        self.container.when(ReportController).needs(Logger).give(FileLogger)
        self.container.when(UserController).needs(Logger).give(DbLogger)

        report = self.container.make(ReportController)
        user = self.container.make(UserController)

        self.assertEqual(report.logger.log('hi'), 'FILE: hi')
        self.assertEqual(user.logger.log('hi'), 'DB: hi')

    def test_contextual_binding_overrides_regular_binding(self):
        self.container.bind(Logger, DbLogger)
        self.container.when(ReportController).needs(Logger).give(FileLogger)

        report = self.container.make(ReportController)
        self.assertIsInstance(report.logger, FileLogger)

    def test_falls_back_to_regular_binding_when_no_contextual_override(self):
        self.container.bind(Logger, FileLogger)

        class PlainController:
            def __init__(self, logger: Logger):
                self.logger = logger

        # Local classes aren't importable by their dotted path, so bind explicitly
        # (mirrors how the container is normally used for non-module-level classes).
        self.container.bind(PlainController, PlainController)
        plain = self.container.make(PlainController)
        self.assertIsInstance(plain.logger, FileLogger)

    def test_give_with_instance_value(self):
        file_logger_instance = FileLogger()
        self.container.when(ReportController).needs(Logger).give(file_logger_instance)

        report = self.container.make(ReportController)
        self.assertIs(report.logger, file_logger_instance)

    def test_give_before_needs_raises(self):
        builder = ContextualBindingBuilder(self.container, 'some.key')
        with self.assertRaises(BindingResolutionException):
            builder.give(FileLogger)

    def test_get_contextual_concrete_returns_none_when_unset(self):
        result = self.container.get_contextual_concrete('nonexistent.key', 'nonexistent.abstract')
        self.assertIsNone(result)


# ─── Tagging ──────────────────────────────────────────────────────────────────

class ContainerTaggingTest(UnitTestCase):

    def before_each(self):
        self.container = Container()

    def test_tag_single_abstract(self):
        self.container.tag(ServiceA, 'reports')
        tagged = self.container.tagged('reports')
        self.assertEqual(len(tagged), 1)
        self.assertIsInstance(tagged[0], ServiceA)

    def test_tag_multiple_abstracts_at_once(self):
        self.container.tag([ServiceA, ServiceB], 'reports')
        tagged = self.container.tagged('reports')
        names = sorted(s.name() for s in tagged)
        self.assertEqual(names, ['A', 'B'])

    def test_tagged_returns_empty_list_for_unknown_tag(self):
        self.assertEqual(self.container.tagged('does_not_exist'), [])

    def test_tag_does_not_duplicate_same_abstract(self):
        self.container.tag(ServiceA, 'reports')
        self.container.tag(ServiceA, 'reports')
        self.assertEqual(len(self.container._tags['reports']), 1)

    def test_multiple_tags_on_same_service(self):
        self.container.tag(ServiceA, 'reports', 'extra')
        self.assertEqual(len(self.container.tagged('reports')), 1)
        self.assertEqual(len(self.container.tagged('extra')), 1)

    def test_tagged_instances_resolve_through_bindings(self):
        self.container.bind(ServiceA, FileLogger)  # rebind ServiceA's key to FileLogger concrete
        self.container.tag(ServiceA, 'misc')
        tagged = self.container.tagged('misc')
        self.assertIsInstance(tagged[0], FileLogger)


if __name__ == '__main__':
    unittest.main()
