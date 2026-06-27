"""
Unit Test: Vector Similarity Search
Tests Blueprint.vector() column definition and
QueryBuilder.order_by_similarity() SQL generation for pgvector-backed
semantic search.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import unittest
from laraflask.testing.test_case import UnitTestCase
from laraflask.orm.model import Model, QueryBuilder
from laraflask.orm.migration import Blueprint


class BlueprintVectorColumnTest(UnitTestCase):

    def test_vector_column_has_correct_type_and_dimensions(self):
        bp = Blueprint('documents')
        bp.vector('embedding', dimensions=384)
        col = bp.get_columns()[0]
        self.assertEqual(col.name, 'embedding')
        self.assertEqual(col.type.dim, 384)

    def test_vector_column_defaults_to_1536_dimensions(self):
        bp = Blueprint('documents')
        bp.vector('embedding')
        col = bp.get_columns()[0]
        self.assertEqual(col.type.dim, 1536)

    def test_vector_column_is_nullable(self):
        bp = Blueprint('documents')
        bp.vector('embedding')
        col = bp.get_columns()[0]
        self.assertTrue(col.nullable)

    def test_vector_combines_with_other_column_types(self):
        bp = Blueprint('documents')
        bp.id()
        bp.string('title')
        bp.vector('embedding', dimensions=128)
        cols = bp.get_columns()
        self.assertEqual(len(cols), 3)
        self.assertEqual(cols[2].name, 'embedding')


class OrderBySimilarityTest(UnitTestCase):

    class Document(Model):
        __table__ = 'documents'
        __fillable__ = ['title', 'embedding']

        @classmethod
        def _get_db_model(cls):
            from sqlalchemy import Column, Integer, String
            from sqlalchemy.orm import declarative_base
            from pgvector.sqlalchemy import Vector

            if not hasattr(OrderBySimilarityTest, '_db_model_cache'):
                Base = declarative_base()

                class DocumentDb(Base):
                    __tablename__ = 'documents'
                    id = Column(Integer, primary_key=True)
                    title = Column(String(255))
                    embedding = Column(Vector(3))

                OrderBySimilarityTest._db_model_cache = DocumentDb
            return OrderBySimilarityTest._db_model_cache

    def test_default_metric_is_cosine(self):
        qb = QueryBuilder(self.Document).order_by_similarity('embedding', [0.1, 0.2, 0.3])
        query = qb._build_query()
        self.assertIn('<=>', str(query))

    def test_l2_metric_uses_correct_operator(self):
        qb = QueryBuilder(self.Document).order_by_similarity('embedding', [0.1, 0.2, 0.3], metric='l2')
        query = qb._build_query()
        self.assertIn('<->', str(query))

    def test_inner_product_metric_uses_correct_operator(self):
        qb = QueryBuilder(self.Document).order_by_similarity(
            'embedding', [0.1, 0.2, 0.3], metric='inner_product'
        )
        query = qb._build_query()
        self.assertIn('<#>', str(query))

    def test_invalid_metric_raises_value_error(self):
        with self.assertRaises(ValueError):
            QueryBuilder(self.Document).order_by_similarity('embedding', [0.1, 0.2], metric='manhattan')

    def test_default_limit_applied_from_similarity_call(self):
        qb = QueryBuilder(self.Document).order_by_similarity('embedding', [0.1, 0.2, 0.3], limit=7)
        self.assertEqual(qb._limit_val, 7)

    def test_explicit_limit_takes_priority_over_similarity_default(self):
        qb = QueryBuilder(self.Document).limit(50).order_by_similarity(
            'embedding', [0.1, 0.2, 0.3], limit=7
        )
        self.assertEqual(qb._limit_val, 50)

    def test_chainable_with_where(self):
        qb = (QueryBuilder(self.Document)
              .where('title', 'LIKE', '%test%')
              .order_by_similarity('embedding', [0.1, 0.2, 0.3]))
        query = qb._build_query()
        sql = str(query)
        self.assertIn('title', sql)
        self.assertIn('<=>', sql)


if __name__ == '__main__':
    unittest.main()
