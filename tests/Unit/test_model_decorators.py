"""
Unit Test: Decorator-based Model Config
Tests @table, @hidden, @fillable decorators as an alternative to manually
declaring __table__/__hidden__/__fillable__, while confirming the old
class-attribute style still works unchanged (backward compatibility).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import unittest
from laraflask.testing.test_case import UnitTestCase
from laraflask.orm.model import Model, table, hidden, fillable


class TableDecoratorTest(UnitTestCase):

    def test_sets_table_name(self):
        @table(name='custom_users')
        class DecoratedA(Model):
            pass
        self.assertEqual(DecoratedA.__table__, 'custom_users')

    def test_sets_primary_key_when_given(self):
        @table(name='custom_users', primary_key='user_id')
        class DecoratedB(Model):
            pass
        self.assertEqual(DecoratedB.__primary_key__, 'user_id')

    def test_default_primary_key_unchanged_when_not_given(self):
        @table(name='posts')
        class DecoratedC(Model):
            pass
        self.assertEqual(DecoratedC.__primary_key__, 'id')

    def test_overrides_auto_inferred_table_name(self):
        @table(name='totally_custom')
        class SomeWeirdName(Model):
            pass
        self.assertEqual(SomeWeirdName.__table__, 'totally_custom')


class HiddenDecoratorTest(UnitTestCase):

    def test_sets_hidden_fields(self):
        @hidden('password', 'remember_token')
        class DecoratedD(Model):
            pass
        self.assertEqual(DecoratedD.__hidden__, ['password', 'remember_token'])

    def test_hidden_fields_excluded_from_to_dict(self):
        @hidden('password')
        class DecoratedE(Model):
            pass
        instance = DecoratedE(name='Rio', password='secret')
        data = instance.to_dict()
        self.assertNotIn('password', data)
        self.assertEqual(data['name'], 'Rio')


class FillableDecoratorTest(UnitTestCase):

    def test_sets_fillable_fields(self):
        @fillable('name', 'email')
        class DecoratedF(Model):
            pass
        self.assertEqual(DecoratedF.__fillable__, ['name', 'email'])


class DecoratorStackingTest(UnitTestCase):

    def test_decorators_can_be_combined(self):
        @table(name='custom_users', primary_key='user_id')
        @hidden('password')
        @fillable('name', 'email')
        class FullyDecorated(Model):
            pass

        self.assertEqual(FullyDecorated.__table__, 'custom_users')
        self.assertEqual(FullyDecorated.__primary_key__, 'user_id')
        self.assertEqual(FullyDecorated.__hidden__, ['password'])
        self.assertEqual(FullyDecorated.__fillable__, ['name', 'email'])

    def test_decorated_model_instantiates_normally(self):
        @table(name='custom_users')
        @hidden('password')
        @fillable('name', 'email')
        class FullyDecorated2(Model):
            pass

        instance = FullyDecorated2(name='Rio', email='rio@example.com', password='secret')
        data = instance.to_dict()
        self.assertEqual(data, {'name': 'Rio', 'email': 'rio@example.com'})


class BackwardCompatibilityTest(UnitTestCase):
    """Models using the old manual class-attribute style must keep working unchanged."""

    def test_manual_table_attribute_still_works(self):
        class OldStyleA(Model):
            __table__ = 'old_users'
        self.assertEqual(OldStyleA.__table__, 'old_users')

    def test_manual_hidden_attribute_still_works(self):
        class OldStyleB(Model):
            __table__ = 'old_users'
            __hidden__ = ['password']
        instance = OldStyleB(name='Rio', password='secret')
        self.assertNotIn('password', instance.to_dict())

    def test_manual_fillable_attribute_still_works(self):
        class OldStyleC(Model):
            __table__ = 'old_users'
            __fillable__ = ['name']
        self.assertEqual(OldStyleC.__fillable__, ['name'])

    def test_auto_inferred_table_name_still_works_without_decorator_or_attribute(self):
        class Article(Model):
            pass
        self.assertEqual(Article.__table__, 'articles')


if __name__ == '__main__':
    unittest.main()
