"""
Unit Test: Cache::touch()
Tests TTL extension without re-fetching the value, across the Array,
File, and Database drivers, plus the default CacheDriver fallback.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import time
import shutil
import unittest
from laraflask.testing.test_case import UnitTestCase
from laraflask.cache.cache import Cache, ArrayDriver, FileDriver, CacheDriver


class ArrayDriverTouchTest(UnitTestCase):

    def before_each(self):
        self.driver = ArrayDriver()

    def test_touch_extends_ttl_without_changing_value(self):
        self.driver.put('foo', {'n': 42}, seconds=10)
        before = self.driver._store['foo']['expires_at']
        time.sleep(0.02)
        ok = self.driver.touch('foo', 1000)
        after = self.driver._store['foo']['expires_at']

        self.assertTrue(ok)
        self.assertGreater(after, before)
        self.assertEqual(self.driver.get('foo'), {'n': 42})

    def test_touch_returns_false_for_missing_key(self):
        self.assertFalse(self.driver.touch('nope', 100))


class FileDriverTouchTest(UnitTestCase):

    def before_each(self):
        self.test_dir = '/tmp/laraflask_test_cache_touch'
        shutil.rmtree(self.test_dir, ignore_errors=True)
        self.driver = FileDriver(self.test_dir)

    def after_each(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_touch_extends_ttl_without_unpickling_via_get(self):
        self.driver.put('foo', {'complex': ['a', 'b'], 'n': 7}, seconds=10)
        before = self.driver._read('foo')['expires_at']
        time.sleep(0.02)

        ok = self.driver.touch('foo', 1000)
        after = self.driver._read('foo')['expires_at']

        self.assertTrue(ok)
        self.assertGreater(after, before)
        self.assertEqual(self.driver.get('foo'), {'complex': ['a', 'b'], 'n': 7})

    def test_touch_returns_false_for_missing_key(self):
        self.assertFalse(self.driver.touch('does-not-exist', 100))


class DefaultDriverTouchFallbackTest(UnitTestCase):
    """The base CacheDriver.touch() falls back to get()+put() for drivers that don't override it."""

    class DummyDriver(CacheDriver):
        def __init__(self):
            self._store = {}

        def get(self, key):
            return self._store.get(key)

        def put(self, key, value, seconds=None):
            self._store[key] = value
            return True

        def has(self, key):
            return key in self._store

        def forget(self, key):
            return bool(self._store.pop(key, None))

        def flush(self):
            self._store.clear()
            return True

        def increment(self, key, value=1):
            self._store[key] = self._store.get(key, 0) + value
            return self._store[key]

        def decrement(self, key, value=1):
            return self.increment(key, -value)

    def before_each(self):
        self.driver = self.DummyDriver()

    def test_fallback_touch_preserves_value(self):
        self.driver.put('x', 'hello')
        ok = self.driver.touch('x', 50)
        self.assertTrue(ok)
        self.assertEqual(self.driver.get('x'), 'hello')

    def test_fallback_touch_returns_false_for_missing_key(self):
        self.assertFalse(self.driver.touch('missing', 50))


class CacheFacadeTouchTest(UnitTestCase):

    def before_each(self):
        Cache.configure(default='array')
        Cache.flush()

    def test_facade_touch_extends_ttl(self):
        Cache.put('session:1', 'data', seconds=10)
        ok = Cache.touch('session:1', 9999)
        self.assertTrue(ok)
        self.assertEqual(Cache.get('session:1'), 'data')

    def test_facade_touch_missing_key_returns_false(self):
        self.assertFalse(Cache.touch('nonexistent', 100))


if __name__ == '__main__':
    unittest.main()
