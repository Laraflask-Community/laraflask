"""
Unit Test: Macroable
Tests dynamic runtime method registration via the Macroable mixin,
including its integration with QueryBuilder.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import unittest
from laraflask.testing.test_case import UnitTestCase
from laraflask.core.macroable import Macroable
from laraflask.orm.model import Model, QueryBuilder


class Money(Macroable):
    def __init__(self, amount):
        self.amount = amount


class Distance(Macroable):
    def __init__(self, meters):
        self.meters = meters


class StringHelpers:
    def shout(self):
        return self.formatted().upper()


class MacroableBasicsTest(UnitTestCase):

    def after_each(self):
        Money.flush_macros()
        Distance.flush_macros()

    def test_macro_registers_callable_method(self):
        Money.macro('double', lambda self: Money(self.amount * 2))
        m = Money(50)
        self.assertEqual(m.double().amount, 100)

    def test_macro_can_accept_extra_arguments(self):
        Money.macro('add', lambda self, other: Money(self.amount + other))
        m = Money(50)
        self.assertEqual(m.add(25).amount, 75)

    def test_has_macro_true_after_registration(self):
        Money.macro('double', lambda self: self)
        self.assertTrue(Money.has_macro('double'))

    def test_has_macro_false_before_registration(self):
        self.assertFalse(Money.has_macro('triple'))

    def test_macros_are_isolated_between_sibling_subclasses(self):
        Money.macro('double', lambda self: Money(self.amount * 2))
        self.assertFalse(Distance.has_macro('double'))
        with self.assertRaises(AttributeError):
            Distance(5).double()

    def test_flush_macros_removes_registered_methods(self):
        Money.macro('double', lambda self: Money(self.amount * 2))
        Money.flush_macros()
        self.assertFalse(Money.has_macro('double'))
        with self.assertRaises(AttributeError):
            Money(10).double()

    def test_macro_overwrites_existing_macro_of_same_name(self):
        Money.macro('label', lambda self: 'first')
        Money.macro('label', lambda self: 'second')
        self.assertEqual(Money(1).label(), 'second')


class MacroableMixinTest(UnitTestCase):

    def after_each(self):
        Money.flush_macros()

    def test_mixin_registers_all_public_methods(self):
        Money.macro('formatted', lambda self: f"Rp {self.amount:,}")
        Money.mixin(StringHelpers)
        m = Money(50000)
        self.assertEqual(m.shout(), 'RP 50,000')

    def test_mixin_replace_false_skips_existing_macros(self):
        Money.macro('shout', lambda self: 'original')
        Money.mixin(StringHelpers, replace=False)
        # 'shout' should remain the originally-registered macro, not StringHelpers'.
        self.assertEqual(Money(1).shout(), 'original')


class QueryBuilderMacroableIntegrationTest(UnitTestCase):
    """Confirm QueryBuilder itself supports macro() as described in the framework's use case."""

    class Article(Model):
        __table__ = 'articles'
        __fillable__ = ['title', 'active']

    def after_each(self):
        QueryBuilder.flush_macros()

    def test_query_builder_is_macroable(self):
        self.assertTrue(issubclass(QueryBuilder, Macroable))

    def test_where_active_macro_appends_correct_where_clause(self):
        QueryBuilder.macro('whereActive', lambda self: self.where('active', True))
        qb = QueryBuilder(self.Article).whereActive()
        self.assertEqual(qb._wheres[0]['column'], 'active')
        self.assertEqual(qb._wheres[0]['value'], True)

    def test_macro_is_chainable_with_existing_methods(self):
        QueryBuilder.macro('whereActive', lambda self: self.where('active', True))
        qb = QueryBuilder(self.Article).whereActive().order_by('title')
        self.assertEqual(len(qb._wheres), 1)
        self.assertEqual(qb._order_bys[0]['column'], 'title')


if __name__ == '__main__':
    unittest.main()
