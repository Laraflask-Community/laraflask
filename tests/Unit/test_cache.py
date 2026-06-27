"""
Unit Test: Cache System
Tests File, Array, and TaggedCache drivers.
"""

import sys, os, tempfile, shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import time
import unittest
from laraflask.testing.test_case import UnitTestCase
from laraflask.cache.cache import Cache, FileDriver, ArrayDriver, TaggedCache


class ArrayDriverTest(UnitTestCase):
    """Test in-memory array cache driver."""

    def before_each(self):
        self.driver = ArrayDriver()

    def test_put_and_get(self):
        self.driver.put('key', 'value')
        self.assertEqual(self.driver.get('key'), 'value')

    def test_get_missing_returns_none(self):
        self.assertIsNone(self.driver.get('nonexistent'))

    def test_has_returns_true_for_existing(self):
        self.driver.put('key', 'val')
        self.assertTrue(self.driver.has('key'))

    def test_has_returns_false_for_missing(self):
        self.assertFalse(self.driver.has('missing'))

    def test_forget_removes_key(self):
        self.driver.put('key', 'val')
        self.driver.forget('key')
        self.assertIsNone(self.driver.get('key'))

    def test_flush_clears_all(self):
        self.driver.put('a', 1)
        self.driver.put('b', 2)
        self.driver.flush()
        self.assertIsNone(self.driver.get('a'))
        self.assertIsNone(self.driver.get('b'))

    def test_expiry_works(self):
        self.driver.put('temp', 'value', seconds=1)
        self.assertEqual(self.driver.get('temp'), 'value')
        # Manually expire
        self.driver._store['temp']['expires_at'] = time.time() - 1
        self.assertIsNone(self.driver.get('temp'))

    def test_put_without_expiry_is_permanent(self):
        self.driver.put('perm', 'forever', seconds=None)
        entry = self.driver._store['perm']
        self.assertIsNone(entry['expires_at'])

    def test_increment(self):
        self.driver.put('counter', 0)
        result = self.driver.increment('counter', 1)
        self.assertEqual(result, 1)
        result = self.driver.increment('counter', 4)
        self.assertEqual(result, 5)

    def test_decrement(self):
        self.driver.put('counter', 10)
        result = self.driver.decrement('counter', 3)
        self.assertEqual(result, 7)

    def test_increment_missing_key_starts_from_zero(self):
        result = self.driver.increment('new_counter', 5)
        self.assertEqual(result, 5)

    def test_store_various_types(self):
        self.driver.put('list', [1, 2, 3])
        self.assertEqual(self.driver.get('list'), [1, 2, 3])

        self.driver.put('dict', {'a': 1})
        self.assertEqual(self.driver.get('dict'), {'a': 1})

        self.driver.put('none', None)
        self.assertIsNone(self.driver.get('none'))

    def test_overwrite_existing_key(self):
        self.driver.put('key', 'first')
        self.driver.put('key', 'second')
        self.assertEqual(self.driver.get('key'), 'second')


class FileDriverTest(UnitTestCase):
    """Test file-based cache driver."""

    def before_each(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.driver = FileDriver(path=self.tmp_dir)

    def after_each(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_put_and_get(self):
        self.driver.put('hello', 'world')
        self.assertEqual(self.driver.get('hello'), 'world')

    def test_complex_object(self):
        data = {'nested': {'key': [1, 2, 3]}, 'count': 42}
        self.driver.put('complex', data)
        result = self.driver.get('complex')
        self.assertEqual(result, data)

    def test_has(self):
        self.driver.put('exists', True)
        self.assertTrue(self.driver.has('exists'))
        self.assertFalse(self.driver.has('missing'))

    def test_forget(self):
        self.driver.put('temp', 'data')
        self.driver.forget('temp')
        self.assertFalse(self.driver.has('temp'))

    def test_flush(self):
        self.driver.put('a', 1)
        self.driver.put('b', 2)
        self.driver.flush()
        self.assertFalse(self.driver.has('a'))

    def test_expired_key_returns_none(self):
        self.driver.put('exp', 'data', seconds=1)
        # Fast-expire by manipulating the stored data
        import pickle
        path = self.driver._key_path('exp')
        with open(path, 'rb') as f:
            data = pickle.load(f)
        data['expires_at'] = time.time() - 1
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        self.assertIsNone(self.driver.get('exp'))

    def test_increment_and_decrement(self):
        self.driver.put('n', 10)
        self.assertEqual(self.driver.increment('n', 5), 15)
        self.assertEqual(self.driver.decrement('n', 3), 12)

    def test_missing_key_increment(self):
        result = self.driver.increment('new_n')
        self.assertEqual(result, 1)

    def test_key_path_uses_hash(self):
        path1 = self.driver._key_path('key_a')
        path2 = self.driver._key_path('key_b')
        self.assertNotEqual(path1, path2)


class CacheFacadeTest(UnitTestCase):
    """Test Cache facade using array driver."""

    def before_each(self):
        Cache.configure(default='array')
        Cache._stores.clear()
        Cache._stores['array'] = ArrayDriver()

    def test_put_and_get(self):
        Cache.put('name', 'Laraflask')
        self.assertEqual(Cache.get('name'), 'Laraflask')

    def test_set_alias(self):
        Cache.set('alias', 'works')
        self.assertEqual(Cache.get('alias'), 'works')

    def test_get_with_default(self):
        val = Cache.get('missing', 'default_val')
        self.assertEqual(val, 'default_val')

    def test_get_with_callable_default(self):
        val = Cache.get('missing', lambda: 'computed')
        self.assertEqual(val, 'computed')

    def test_has_and_missing(self):
        Cache.put('present', True)
        self.assertTrue(Cache.has('present'))
        self.assertFalse(Cache.missing('present'))
        self.assertFalse(Cache.has('absent'))
        self.assertTrue(Cache.missing('absent'))

    def test_forget(self):
        Cache.put('bye', 'bye')
        Cache.forget('bye')
        self.assertIsNone(Cache.get('bye'))

    def test_forever(self):
        Cache.forever('eternal', 42)
        self.assertEqual(Cache.get('eternal'), 42)

    def test_remember(self):
        called = [0]
        def compute():
            called[0] += 1
            return 'computed_value'

        result1 = Cache.remember('r', 60, compute)
        result2 = Cache.remember('r', 60, compute)
        self.assertEqual(result1, 'computed_value')
        self.assertEqual(result2, 'computed_value')
        self.assertEqual(called[0], 1)  # callback called only once

    def test_remember_forever(self):
        result = Cache.remember_forever('rf', lambda: 'forever')
        self.assertEqual(result, 'forever')
        # Second call uses cached value
        result2 = Cache.remember_forever('rf', lambda: 'different')
        self.assertEqual(result2, 'forever')

    def test_pull_removes_after_get(self):
        Cache.put('temp', 'data')
        val = Cache.pull('temp')
        self.assertEqual(val, 'data')
        self.assertFalse(Cache.has('temp'))

    def test_pull_missing_returns_default(self):
        val = Cache.pull('nonexistent', 'fallback')
        self.assertEqual(val, 'fallback')

    def test_add_only_stores_when_missing(self):
        Cache.add('once', 'first', 60)
        Cache.add('once', 'second', 60)
        self.assertEqual(Cache.get('once'), 'first')

    def test_increment(self):
        Cache.put('n', 5)
        Cache.increment('n', 3)
        self.assertEqual(Cache.get('n'), 8)

    def test_decrement(self):
        Cache.put('n', 10)
        Cache.decrement('n', 4)
        self.assertEqual(Cache.get('n'), 6)

    def test_flush(self):
        Cache.put('a', 1)
        Cache.put('b', 2)
        Cache.flush()
        self.assertFalse(Cache.has('a'))

    def test_put_many(self):
        Cache.put_many({'x': 1, 'y': 2, 'z': 3}, seconds=60)
        self.assertEqual(Cache.get('x'), 1)
        self.assertEqual(Cache.get('y'), 2)
        self.assertEqual(Cache.get('z'), 3)

    def test_many(self):
        Cache.put('p', 'one')
        Cache.put('q', 'two')
        result = Cache.many(['p', 'q', 'missing'])
        self.assertEqual(result['p'], 'one')
        self.assertEqual(result['q'], 'two')
        self.assertIsNone(result['missing'])


class TaggedCacheTest(UnitTestCase):
    """Test tag-based cache invalidation."""

    def before_each(self):
        self.driver = ArrayDriver()

    def test_put_and_get_with_tags(self):
        tagged = TaggedCache(self.driver, ['posts'])
        tagged.put('featured', 'data', 60)
        self.assertEqual(tagged.get('featured'), 'data')

    def test_tags_isolate_keys(self):
        posts = TaggedCache(self.driver, ['posts'])
        users = TaggedCache(self.driver, ['users'])
        posts.put('count', 10)
        users.put('count', 99)
        self.assertEqual(posts.get('count'), 10)
        self.assertEqual(users.get('count'), 99)

    def test_forget_tagged_key(self):
        tagged = TaggedCache(self.driver, ['blog'])
        tagged.put('popular', [1, 2, 3])
        tagged.forget('popular')
        self.assertIsNone(tagged.get('popular'))

    def test_tagged_remember(self):
        tagged = TaggedCache(self.driver, ['expensive'])
        result = tagged.remember('data', 60, lambda: {'expensive': True})
        self.assertEqual(result, {'expensive': True})
        # Second call uses cache
        result2 = tagged.remember('data', 60, lambda: {'cheap': True})
        self.assertEqual(result2, {'expensive': True})

    def test_multi_tag_prefix(self):
        t1 = TaggedCache(self.driver, ['a', 'b'])
        t2 = TaggedCache(self.driver, ['b', 'a'])
        t1.put('key', 'val1')
        # Same tags (sorted), should share cache
        self.assertEqual(t2.get('key'), 'val1')


if __name__ == '__main__':
    unittest.main()
