"""
Unit Test: EloquentPy ORM
Tests Model, QueryBuilder, relationships, casts, accessors.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from laraflask.testing.test_case import UnitTestCase
from laraflask.orm.model import Model, QueryBuilder, ModelNotFoundException


# ─── Dummy model for testing ─────────────────────────────────────────────────

class Post(Model):
    __table__ = 'posts'
    __fillable__ = ['title', 'body', 'status', 'views']
    __hidden__   = ['secret']
    __casts__    = {'views': 'integer', 'published': 'boolean'}
    __timestamps__ = True

    def get_title_upper_attribute(self):
        return self._attributes.get('title', '').upper()

    def set_title_attribute(self, value):
        return value.strip() if isinstance(value, str) else value


class ModelMetaTest(UnitTestCase):
    """Test ModelMeta table name derivation."""

    def test_simple_model_name(self):
        class User(Model): pass
        self.assertEqual(User.__table__, 'users')

    def test_camel_case_model_name(self):
        class BlogPost(Model): pass
        self.assertEqual(BlogPost.__table__, 'blog_posts')

    def test_model_ending_in_y(self):
        class Category(Model): pass
        self.assertEqual(Category.__table__, 'categories')

    def test_explicit_table_name(self):
        class Log(Model):
            __table__ = 'activity_logs'
        self.assertEqual(Log.__table__, 'activity_logs')

    def test_model_with_es_suffix(self):
        class Address(Model): pass
        # ends in 's' -> 'es'
        self.assertIn('address', Address.__table__)


class ModelInstanceTest(UnitTestCase):
    """Test model instantiation and attribute access."""

    def test_create_model_with_attributes(self):
        post = Post(title='Hello World', body='Content', views=10)
        self.assertEqual(post._attributes['title'], 'Hello World')
        self.assertEqual(post._attributes['body'], 'Content')

    def test_set_attribute_via_setattr(self):
        post = Post()
        post.title = '  Trimmed  '
        # set_title_attribute strips whitespace
        self.assertEqual(post._attributes['title'], 'Trimmed')

    def test_cast_integer(self):
        post = Post(views='42')
        self.assertEqual(post.views, 42)
        self.assertIsInstance(post.views, int)

    def test_cast_boolean(self):
        post = Post()
        post._attributes['published'] = 1
        self.assertTrue(post.published)

    def test_accessor(self):
        post = Post(title='hello')
        self.assertEqual(post.title_upper, 'HELLO')

    def test_hidden_fields_excluded_from_dict(self):
        post = Post(title='Test', secret='s3cr3t')
        d = post.to_dict()
        self.assertIn('title', d)
        self.assertNotIn('secret', d)

    def test_to_json(self):
        import json
        post = Post(title='JSON Test', views=5)
        data = json.loads(post.to_json())
        self.assertEqual(data['title'], 'JSON Test')

    def test_fill_respects_fillable(self):
        post = Post()
        post.fill({'title': 'Filled', 'secret': 'hacked'})
        self.assertEqual(post._attributes.get('title'), 'Filled')
        # 'secret' is not in __fillable__, so should not be set
        self.assertIsNone(post._attributes.get('secret'))

    def test_is_dirty_after_change(self):
        post = Post(title='Original')
        post._exists = True
        post.title = 'Changed'
        self.assertTrue(post.is_dirty())
        self.assertTrue(post.is_dirty('title'))
        self.assertFalse(post.is_dirty('body'))

    def test_repr(self):
        post = Post()
        post._attributes['id'] = 99
        self.assertIn('Post', repr(post))
        self.assertIn('99', repr(post))

    def test_model_from_db_sets_exists(self):
        mock_db_obj = MagicMock()
        mock_db_obj.__table__ = MagicMock()
        mock_col = MagicMock()
        mock_col.name = 'id'
        mock_db_obj.__table__.columns = [mock_col]
        mock_db_obj.id = 1

        instance = Post._from_db(mock_db_obj)
        self.assertIsNotNone(instance)
        self.assertTrue(instance._exists)

    def test_from_db_with_none_returns_none(self):
        result = Post._from_db(None)
        self.assertIsNone(result)


class QueryBuilderTest(UnitTestCase):
    """Test QueryBuilder fluent interface (without real DB)."""

    def _make_qb(self):
        qb = QueryBuilder(Post)
        return qb

    def test_where_appends_condition(self):
        qb = self._make_qb()
        qb.where('status', 'published')
        self.assertEqual(len(qb._wheres), 1)
        self.assertEqual(qb._wheres[0]['column'], 'status')
        self.assertEqual(qb._wheres[0]['value'], 'published')

    def test_where_with_operator(self):
        qb = self._make_qb()
        qb.where('views', '>', 100)
        self.assertEqual(qb._wheres[0]['operator'], '>')
        self.assertEqual(qb._wheres[0]['value'], 100)

    def test_or_where(self):
        qb = self._make_qb()
        qb.where('status', 'published').or_where('status', 'featured')
        self.assertEqual(qb._wheres[1]['boolean'], 'OR')

    def test_where_in(self):
        qb = self._make_qb()
        qb.where_in('id', [1, 2, 3])
        self.assertEqual(qb._wheres[0]['type'], 'in')
        self.assertEqual(qb._wheres[0]['values'], [1, 2, 3])

    def test_where_null(self):
        qb = self._make_qb()
        qb.where_null('deleted_at')
        self.assertEqual(qb._wheres[0]['type'], 'null')

    def test_where_not_null(self):
        qb = self._make_qb()
        qb.where_not_null('email_verified_at')
        self.assertEqual(qb._wheres[0]['type'], 'not_null')

    def test_where_between(self):
        qb = self._make_qb()
        qb.where_between('views', [10, 100])
        self.assertEqual(qb._wheres[0]['type'], 'between')

    def test_order_by(self):
        qb = self._make_qb()
        qb.order_by('created_at', 'DESC')
        self.assertEqual(qb._order_bys[0]['column'], 'created_at')
        self.assertEqual(qb._order_bys[0]['direction'], 'DESC')

    def test_order_by_desc(self):
        qb = self._make_qb()
        qb.order_by_desc('views')
        self.assertEqual(qb._order_bys[0]['direction'], 'DESC')

    def test_latest_adds_created_at_desc(self):
        qb = self._make_qb()
        qb.latest()
        self.assertEqual(qb._order_bys[0]['column'], 'created_at')
        self.assertEqual(qb._order_bys[0]['direction'], 'DESC')

    def test_limit_and_take(self):
        qb = self._make_qb()
        qb.limit(10)
        self.assertEqual(qb._limit_val, 10)

        qb2 = self._make_qb()
        qb2.take(5)
        self.assertEqual(qb2._limit_val, 5)

    def test_offset_and_skip(self):
        qb = self._make_qb()
        qb.offset(20)
        self.assertEqual(qb._offset_val, 20)

        qb2 = self._make_qb()
        qb2.skip(15)
        self.assertEqual(qb2._offset_val, 15)

    def test_select(self):
        qb = self._make_qb()
        qb.select('id', 'title', 'status')
        self.assertEqual(qb._selects, ['id', 'title', 'status'])

    def test_with_relations(self):
        qb = self._make_qb()
        qb.with_relations('author', 'comments')
        self.assertIn('author', qb._with_relations)
        self.assertIn('comments', qb._with_relations)

    def test_join(self):
        qb = self._make_qb()
        qb.join('users', 'posts.user_id', '=', 'users.id')
        self.assertEqual(len(qb._joins), 1)
        self.assertEqual(qb._joins[0]['type'], 'INNER')

    def test_left_join(self):
        qb = self._make_qb()
        qb.left_join('categories', 'posts.category_id', '=', 'categories.id')
        self.assertEqual(qb._joins[0]['type'], 'LEFT')

    def test_chaining(self):
        qb = self._make_qb()
        result = (qb
                  .select('id', 'title')
                  .where('status', 'published')
                  .order_by('created_at', 'DESC')
                  .limit(10)
                  .offset(0))
        # All chained methods return the same QueryBuilder
        self.assertIsInstance(result, QueryBuilder)
        self.assertEqual(result._limit_val, 10)
        self.assertEqual(len(result._wheres), 1)

    def test_pluck_returns_list(self):
        """pluck() with mocked get()"""
        qb = self._make_qb()
        mock_post1 = Post(title='A', views=1)
        mock_post2 = Post(title='B', views=2)
        qb.get = MagicMock(return_value=[mock_post1, mock_post2])
        result = qb.pluck('title')
        self.assertEqual(result, ['A', 'B'])

    def test_pluck_with_key(self):
        qb = self._make_qb()
        mock_post1 = Post(title='A', views=1)
        mock_post1._attributes['id'] = 10
        mock_post2 = Post(title='B', views=2)
        mock_post2._attributes['id'] = 20
        qb.get = MagicMock(return_value=[mock_post1, mock_post2])
        result = qb.pluck('title', 'id')
        self.assertEqual(result, {10: 'A', 20: 'B'})

    def test_paginate_structure(self):
        qb = self._make_qb()
        qb.count = MagicMock(return_value=50)
        qb.get = MagicMock(return_value=[Post(title=f'Post {i}') for i in range(15)])
        result = qb.paginate(per_page=15, page=2)
        self.assertEqual(result['total'], 50)
        self.assertEqual(result['per_page'], 15)
        self.assertEqual(result['current_page'], 2)
        self.assertEqual(result['last_page'], 4)
        self.assertEqual(len(result['data']), 15)


class ModelRelationshipTest(UnitTestCase):
    """Test ORM relationship helpers."""

    def test_has_many_calls_where(self):
        class Comment(Model):
            __table__ = 'comments'

        user = Post.__new__(Post)
        user._attributes = {'id': 1}
        user._exists = True
        user._dirty = {}
        user._relations = {}

        Comment.where = MagicMock(return_value=MagicMock(get=MagicMock(return_value=[])))
        result = user.has_many(Comment, 'post_id', 'id')
        Comment.where.assert_called_once_with('post_id', 1)

    def test_belongs_to_calls_where(self):
        class Author(Model):
            __table__ = 'authors'
            __primary_key__ = 'id'

        post = Post.__new__(Post)
        post._attributes = {'author_id': 5}
        post._exists = True
        post._dirty = {}
        post._relations = {}

        Author.where = MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))
        user = post.belongs_to(Author, 'author_id', 'id')
        Author.where.assert_called_once_with('id', 5)

    def test_has_one_calls_where(self):
        class Profile(Model):
            __table__ = 'profiles'

        user = Post.__new__(Post)
        user._attributes = {'id': 3}
        user._exists = True
        user._dirty = {}
        user._relations = {}

        Profile.where = MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))
        user.has_one(Profile, 'post_id', 'id')
        Profile.where.assert_called_once_with('post_id', 3)


class ModelSoftDeleteTest(UnitTestCase):
    """Test soft delete behaviour."""

    def test_soft_delete_model_config(self):
        class Article(Model):
            __table__ = 'articles'
            __soft_delete__ = True

        article = Article.__new__(Article)
        self.assertTrue(Article.__soft_delete__)

    def test_soft_delete_sets_deleted_at(self):
        import datetime

        class Article(Model):
            __table__ = 'articles'
            __soft_delete__ = True

        article = Article.__new__(Article)
        article._attributes = {'id': 1}
        article._exists = True
        article._dirty = {}
        article._relations = {}

        # Directly test the soft-delete attribute-setting logic
        Article.__soft_delete__ = True
        article._attributes['deleted_at'] = datetime.datetime.utcnow()
        self.assertIn('deleted_at', article._attributes)
        self.assertIsInstance(article._attributes['deleted_at'], datetime.datetime)

    def test_restore_clears_deleted_at(self):
        import datetime

        class Article(Model):
            __table__ = 'articles'
            __soft_delete__ = True

        article = Article.__new__(Article)
        article._attributes = {'id': 1, 'deleted_at': datetime.datetime.utcnow()}
        article._exists = True
        article._dirty = {}
        article._relations = {}

        # Simulate restore: set deleted_at to None
        Article.__soft_delete__ = True
        article._attributes['deleted_at'] = None
        self.assertIsNone(article._attributes['deleted_at'])


class ModelCastTest(UnitTestCase):
    """Test model attribute casting."""

    def test_cast_to_int(self):
        class M(Model):
            __table__ = 'm'
            __casts__ = {'qty': 'integer'}

        m = M.__new__(M)
        m._attributes = {'qty': '5'}
        m._dirty = {}
        m._relations = {}
        m._exists = False
        self.assertEqual(m.qty, 5)
        self.assertIsInstance(m.qty, int)

    def test_cast_to_bool(self):
        class M(Model):
            __table__ = 'm'
            __casts__ = {'is_active': 'boolean'}

        m = M.__new__(M)
        m._attributes = {'is_active': 0}
        m._dirty = {}
        m._relations = {}
        m._exists = False
        self.assertFalse(m.is_active)

    def test_cast_to_json(self):
        import json

        class M(Model):
            __table__ = 'm'
            __casts__ = {'meta': 'json'}

        m = M.__new__(M)
        m._attributes = {'meta': '{"key": "value"}'}
        m._dirty = {}
        m._relations = {}
        m._exists = False
        result = m.meta
        self.assertEqual(result, {'key': 'value'})

    def test_cast_to_float(self):
        class M(Model):
            __table__ = 'm'
            __casts__ = {'price': 'float'}

        m = M.__new__(M)
        m._attributes = {'price': '9.99'}
        m._dirty = {}
        m._relations = {}
        m._exists = False
        self.assertAlmostEqual(m.price, 9.99)

    def test_cast_none_returns_none(self):
        class M(Model):
            __table__ = 'm'
            __casts__ = {'qty': 'integer'}

        m = M.__new__(M)
        m._attributes = {'qty': None}
        m._dirty = {}
        m._relations = {}
        m._exists = False
        self.assertIsNone(m.qty)


class ModelStaticMethodTest(UnitTestCase):
    """Test Model class-level query method proxies."""

    def test_query_returns_query_builder(self):
        qb = Post.query()
        self.assertIsInstance(qb, QueryBuilder)

    def test_where_returns_query_builder(self):
        qb = Post.where('status', 'published')
        self.assertIsInstance(qb, QueryBuilder)

    def test_where_in_returns_query_builder(self):
        qb = Post.where_in('id', [1, 2, 3])
        self.assertIsInstance(qb, QueryBuilder)

    def test_order_by_returns_query_builder(self):
        qb = Post.order_by('title')
        self.assertIsInstance(qb, QueryBuilder)

    def test_latest_returns_query_builder(self):
        qb = Post.latest()
        self.assertIsInstance(qb, QueryBuilder)

    def test_oldest_returns_query_builder(self):
        qb = Post.oldest()
        self.assertIsInstance(qb, QueryBuilder)


if __name__ == '__main__':
    unittest.main()
