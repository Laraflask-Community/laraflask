"""
Unit Test: Collection
Tests the chainable Collection wrapper (map, filter, reduce, pluck, etc.)
and its integration with QueryBuilder.get(as_collection=True).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import unittest
from laraflask.testing.test_case import UnitTestCase
from laraflask.core.collection import Collection
from laraflask.orm.model import Model, QueryBuilder


class CollectionConstructionTest(UnitTestCase):

    def test_wraps_list(self):
        c = Collection([1, 2, 3])
        self.assertEqual(c.to_list(), [1, 2, 3])

    def test_wraps_dict(self):
        c = Collection({'a': 1, 'b': 2})
        self.assertEqual(c.to_dict(), {'a': 1, 'b': 2})

    def test_defaults_to_empty_list(self):
        c = Collection()
        self.assertEqual(c.to_list(), [])

    def test_wraps_another_collection(self):
        original = Collection([1, 2, 3])
        copy = Collection(original)
        self.assertEqual(copy.to_list(), [1, 2, 3])

    def test_make_classmethod(self):
        c = Collection.make([1, 2])
        self.assertIsInstance(c, Collection)

    def test_times_without_callback(self):
        c = Collection.times(3)
        self.assertEqual(c.to_list(), [1, 2, 3])

    def test_times_with_callback(self):
        c = Collection.times(3, lambda n: n * 10)
        self.assertEqual(c.to_list(), [10, 20, 30])

    def test_range(self):
        c = Collection.range(2, 5)
        self.assertEqual(c.to_list(), [2, 3, 4, 5])


class CollectionTransformationTest(UnitTestCase):

    def test_map(self):
        c = Collection([1, 2, 3]).map(lambda x: x * 2)
        self.assertEqual(c.to_list(), [2, 4, 6])

    def test_map_on_dict(self):
        c = Collection({'a': 1, 'b': 2}).map(lambda v: v + 1)
        self.assertEqual(c.to_dict(), {'a': 2, 'b': 3})

    def test_map_with_keys(self):
        c = Collection([1, 2, 3]).map_with_keys(lambda x: (f"key_{x}", x * 10))
        self.assertEqual(c.to_dict(), {'key_1': 10, 'key_2': 20, 'key_3': 30})

    def test_filter_default_truthy(self):
        c = Collection([0, 1, '', 'a', None, 2]).filter()
        self.assertEqual(c.to_list(), [1, 'a', 2])

    def test_filter_with_callback(self):
        c = Collection([1, 2, 3, 4]).filter(lambda x: x % 2 == 0)
        self.assertEqual(c.to_list(), [2, 4])

    def test_reject_is_inverse_of_filter(self):
        c = Collection([1, 2, 3, 4]).reject(lambda x: x % 2 == 0)
        self.assertEqual(c.to_list(), [1, 3])

    def test_reduce(self):
        total = Collection([1, 2, 3, 4]).reduce(lambda carry, x: carry + x, 0)
        self.assertEqual(total, 10)

    def test_each_runs_callback_for_every_item(self):
        seen = []
        Collection([1, 2, 3]).each(lambda x: seen.append(x))
        self.assertEqual(seen, [1, 2, 3])

    def test_each_stops_on_false(self):
        seen = []
        def visit(x):
            seen.append(x)
            return x < 2
        Collection([1, 2, 3]).each(visit)
        self.assertEqual(seen, [1, 2])

    def test_pluck_from_dicts(self):
        c = Collection([{'name': 'Rio'}, {'name': 'Budi'}]).pluck('name')
        self.assertEqual(c.to_list(), ['Rio', 'Budi'])

    def test_pluck_with_key_by(self):
        c = Collection([{'id': 1, 'name': 'Rio'}, {'id': 2, 'name': 'Budi'}])
        result = c.pluck('name', key_by='id')
        self.assertEqual(result.to_dict(), {1: 'Rio', 2: 'Budi'})

    def test_pluck_from_objects(self):
        class Item:
            def __init__(self, name): self.name = name
        c = Collection([Item('A'), Item('B')]).pluck('name')
        self.assertEqual(c.to_list(), ['A', 'B'])

    def test_flatten_one_level(self):
        c = Collection([[1, 2], [3, 4]]).flatten()
        self.assertEqual(c.to_list(), [1, 2, 3, 4])

    def test_flatten_nested(self):
        c = Collection([1, [2, [3, 4]], 5]).flatten()
        self.assertEqual(c.to_list(), [1, 2, 3, 4, 5])

    def test_flatten_with_depth(self):
        c = Collection([1, [2, [3, 4]], 5]).flatten(depth=1)
        self.assertEqual(c.to_list(), [1, 2, [3, 4], 5])

    def test_unique_no_key(self):
        c = Collection([1, 2, 2, 3, 1]).unique()
        self.assertEqual(c.to_list(), [1, 2, 3])

    def test_unique_with_key(self):
        items = [{'role': 'admin'}, {'role': 'user'}, {'role': 'admin'}]
        c = Collection(items).unique('role')
        self.assertEqual(c.count(), 2)

    def test_flip(self):
        c = Collection({'a': 1, 'b': 2}).flip()
        self.assertEqual(c.to_dict(), {1: 'a', 2: 'b'})

    def test_merge_lists(self):
        c = Collection([1, 2]).merge([3, 4])
        self.assertEqual(c.to_list(), [1, 2, 3, 4])

    def test_merge_dicts(self):
        c = Collection({'a': 1}).merge({'b': 2})
        self.assertEqual(c.to_dict(), {'a': 1, 'b': 2})


class CollectionOrderingTest(UnitTestCase):

    def test_sort_by_attribute_key(self):
        items = [{'age': 30}, {'age': 20}, {'age': 25}]
        c = Collection(items).sort_by('age')
        self.assertEqual([i['age'] for i in c], [20, 25, 30])

    def test_sort_by_callback(self):
        c = Collection([3, 1, 2]).sort_by(lambda x: x)
        self.assertEqual(c.to_list(), [1, 2, 3])

    def test_sort_by_desc(self):
        c = Collection([1, 3, 2]).sort_by_desc(lambda x: x)
        self.assertEqual(c.to_list(), [3, 2, 1])

    def test_group_by_attribute(self):
        items = [{'role': 'admin'}, {'role': 'user'}, {'role': 'admin'}]
        groups = Collection(items).group_by('role')
        self.assertEqual(groups['admin'].count(), 2)
        self.assertEqual(groups['user'].count(), 1)

    def test_group_by_callback(self):
        groups = Collection([1, 2, 3, 4, 5]).group_by(lambda x: 'even' if x % 2 == 0 else 'odd')
        self.assertEqual(groups['even'].to_list(), [2, 4])
        self.assertEqual(groups['odd'].to_list(), [1, 3, 5])

    def test_chunk(self):
        c = Collection([1, 2, 3, 4, 5]).chunk(2)
        self.assertEqual(c.count(), 3)
        self.assertEqual(c.first().to_list(), [1, 2])
        self.assertEqual(c.last().to_list(), [5])

    def test_reverse(self):
        c = Collection([1, 2, 3]).reverse()
        self.assertEqual(c.to_list(), [3, 2, 1])

    def test_take_positive(self):
        c = Collection([1, 2, 3, 4]).take(2)
        self.assertEqual(c.to_list(), [1, 2])

    def test_take_negative(self):
        c = Collection([1, 2, 3, 4]).take(-2)
        self.assertEqual(c.to_list(), [3, 4])


class CollectionInspectionTest(UnitTestCase):

    def test_contains_value(self):
        self.assertTrue(Collection([1, 2, 3]).contains(2))
        self.assertFalse(Collection([1, 2, 3]).contains(9))

    def test_contains_with_callback(self):
        c = Collection([{'role': 'admin'}, {'role': 'user'}])
        self.assertTrue(c.contains(callback=lambda i: i['role'] == 'admin'))
        self.assertFalse(c.contains(callback=lambda i: i['role'] == 'superadmin'))

    def test_first_without_callback(self):
        self.assertEqual(Collection([1, 2, 3]).first(), 1)

    def test_first_with_callback(self):
        result = Collection([1, 2, 3, 4]).first(lambda x: x > 2)
        self.assertEqual(result, 3)

    def test_first_default_when_empty(self):
        self.assertEqual(Collection([]).first(default='none'), 'none')

    def test_last_without_callback(self):
        self.assertEqual(Collection([1, 2, 3]).last(), 3)

    def test_last_with_callback(self):
        result = Collection([1, 2, 3, 4]).last(lambda x: x < 3)
        self.assertEqual(result, 2)

    def test_count(self):
        self.assertEqual(Collection([1, 2, 3]).count(), 3)

    def test_is_empty(self):
        self.assertTrue(Collection([]).is_empty())
        self.assertFalse(Collection([1]).is_empty())

    def test_is_not_empty(self):
        self.assertTrue(Collection([1]).is_not_empty())


class CollectionAggregationTest(UnitTestCase):

    def test_sum_plain_numbers(self):
        self.assertEqual(Collection([1, 2, 3]).sum(), 6)

    def test_sum_with_key(self):
        items = [{'price': 10}, {'price': 20}]
        self.assertEqual(Collection(items).sum('price'), 30)

    def test_avg(self):
        self.assertEqual(Collection([2, 4, 6]).avg(), 4)

    def test_avg_empty_is_zero(self):
        self.assertEqual(Collection([]).avg(), 0)

    def test_min_and_max_plain(self):
        c = Collection([5, 1, 9, 3])
        self.assertEqual(c.min(), 1)
        self.assertEqual(c.max(), 9)

    def test_min_and_max_with_key(self):
        items = [{'age': 30}, {'age': 20}, {'age': 40}]
        c = Collection(items)
        self.assertEqual(c.min('age')['age'], 20)
        self.assertEqual(c.max('age')['age'], 40)


class CollectionFluentUtilityTest(UnitTestCase):

    def test_tap_does_not_alter_chain(self):
        seen = []
        result = Collection([1, 2, 3]).tap(lambda c: seen.append(c.to_list())).map(lambda x: x + 1)
        self.assertEqual(seen, [[1, 2, 3]])
        self.assertEqual(result.to_list(), [2, 3, 4])

    def test_pipe_transforms_result(self):
        result = Collection([1, 2, 3]).pipe(lambda c: c.sum())
        self.assertEqual(result, 6)

    def test_when_true_applies_callback(self):
        result = Collection([1, 2, 3]).when(True, lambda c: c.map(lambda x: x * 10))
        self.assertEqual(result.to_list(), [10, 20, 30])

    def test_when_false_skips_callback(self):
        result = Collection([1, 2, 3]).when(False, lambda c: c.map(lambda x: x * 10))
        self.assertEqual(result.to_list(), [1, 2, 3])


class CollectionPythonProtocolTest(UnitTestCase):

    def test_iteration(self):
        self.assertEqual(list(Collection([1, 2, 3])), [1, 2, 3])

    def test_len(self):
        self.assertEqual(len(Collection([1, 2, 3])), 3)

    def test_getitem(self):
        c = Collection([10, 20, 30])
        self.assertEqual(c[1], 20)

    def test_setitem(self):
        c = Collection([10, 20, 30])
        c[1] = 99
        self.assertEqual(c.to_list(), [10, 99, 30])

    def test_contains_operator(self):
        c = Collection([1, 2, 3])
        self.assertIn(2, c)
        self.assertNotIn(9, c)

    def test_bool_truthiness(self):
        self.assertTrue(bool(Collection([1])))
        self.assertFalse(bool(Collection([])))

    def test_equality_with_collection(self):
        self.assertEqual(Collection([1, 2]), Collection([1, 2]))

    def test_equality_with_list(self):
        self.assertEqual(Collection([1, 2]), [1, 2])


class QueryBuilderCollectionIntegrationTest(UnitTestCase):
    """Test that QueryBuilder.get(as_collection=True) wraps results, while staying backward compatible."""

    class Article(Model):
        __table__ = 'articles'
        __fillable__ = ['title', 'views']

    def test_get_default_returns_plain_list(self):
        qb = QueryBuilder(self.Article)
        qb._build_query = lambda: None  # simulate no DB connection
        result = qb.get()
        self.assertIsInstance(result, list)

    def test_get_as_collection_returns_collection(self):
        qb = QueryBuilder(self.Article)
        qb._build_query = lambda: None
        result = qb.get(as_collection=True)
        self.assertIsInstance(result, Collection)

    def test_get_as_collection_supports_chaining(self):
        qb = QueryBuilder(self.Article)
        mock_query = type('MockQuery', (), {'all': lambda self: []})()
        qb._build_query = lambda: mock_query
        result = qb.get(as_collection=True)
        self.assertEqual(result.count(), 0)
        self.assertIsInstance(result.map(lambda x: x), Collection)


if __name__ == '__main__':
    unittest.main()
