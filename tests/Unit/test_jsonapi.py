"""
Unit Test: JSON:API Resource
Tests the JsonApiResource transformer against the JSON:API spec structure:
{data, included, links, meta}, sparse fieldsets, and relationship inclusion.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import unittest
from flask import Flask
from laraflask.testing.test_case import UnitTestCase
from laraflask.api.jsonapi import JsonApiResource, JsonApiResourceCollection


# ─── Fixtures ─────────────────────────────────────────────────────────────────

class FakePost:
    __primary_key__ = 'id'

    def __init__(self, id, title):
        self.id = id
        self.title = title

    def to_dict(self):
        return {'id': self.id, 'title': self.title}


class FakeUser:
    __primary_key__ = 'id'

    def __init__(self, id, name, email, posts=None, manager=None):
        self.id = id
        self.name = name
        self.email = email
        self._posts = posts or []
        self._manager = manager

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'email': self.email}

    @property
    def posts(self):
        return self._posts

    @property
    def manager(self):
        return self._manager


class PostResource(JsonApiResource):
    type_ = 'posts'


class UserResource(JsonApiResource):
    type_ = 'users'

    def relationships(self):
        return {'posts': self.model.posts, 'manager': self.model.manager}

    def resource_class_for(self, relation_name, related_model):
        if relation_name == 'posts':
            return PostResource
        return UserResource


# ─── Tests ────────────────────────────────────────────────────────────────────

class JsonApiResourceBasicsTest(UnitTestCase):

    def before_each(self):
        self.app = Flask(__name__)

    def test_to_array_has_type_id_attributes(self):
        with self.app.test_request_context('/'):
            user = FakeUser(1, 'Rio', 'rio@example.com')
            arr = UserResource(user).to_array()
            self.assertEqual(arr['type'], 'users')
            self.assertEqual(arr['id'], '1')
            self.assertEqual(arr['attributes'], {'name': 'Rio', 'email': 'rio@example.com'})

    def test_primary_key_excluded_from_attributes(self):
        with self.app.test_request_context('/'):
            user = FakeUser(1, 'Rio', 'rio@example.com')
            arr = UserResource(user).to_array()
            self.assertNotIn('id', arr['attributes'])

    def test_infers_type_from_class_name_when_not_set(self):
        with self.app.test_request_context('/'):
            class GenericResource(JsonApiResource):
                pass
            res = GenericResource(FakePost(1, 'Hello'))
            self.assertEqual(res.type_, 'fakeposts')


class JsonApiRelationshipsTest(UnitTestCase):

    def before_each(self):
        self.app = Flask(__name__)

    def test_relationship_data_is_resource_identifier(self):
        with self.app.test_request_context('/'):
            post = FakePost(10, 'Hello World')
            user = FakeUser(1, 'Rio', 'rio@example.com', posts=[post])
            arr = UserResource(user).to_array()
            self.assertEqual(
                arr['relationships']['posts']['data'],
                [{'type': 'posts', 'id': '10'}]
            )

    def test_to_one_null_relationship(self):
        with self.app.test_request_context('/'):
            user = FakeUser(1, 'Rio', 'rio@example.com', manager=None)
            arr = UserResource(user).to_array()
            self.assertEqual(arr['relationships']['manager'], {'data': None})

    def test_to_one_relationship_with_value(self):
        with self.app.test_request_context('/'):
            boss = FakeUser(2, 'Budi', 'budi@example.com')
            user = FakeUser(1, 'Rio', 'rio@example.com', manager=boss)
            arr = UserResource(user).to_array()
            self.assertEqual(arr['relationships']['manager']['data'], {'type': 'users', 'id': '2'})


class JsonApiIncludeTest(UnitTestCase):

    def before_each(self):
        self.app = Flask(__name__)

    def test_include_populates_registry(self):
        with self.app.test_request_context('/?include=posts'):
            post = FakePost(10, 'Hello World')
            user = FakeUser(1, 'Rio', 'rio@example.com', posts=[post])
            resource = UserResource(user)
            resource.to_array()
            self.assertIn(('posts', '10'), resource._included_registry)
            self.assertEqual(
                resource._included_registry[('posts', '10')]['attributes']['title'],
                'Hello World'
            )

    def test_no_include_leaves_registry_empty(self):
        with self.app.test_request_context('/'):
            post = FakePost(10, 'Hello World')
            user = FakeUser(1, 'Rio', 'rio@example.com', posts=[post])
            resource = UserResource(user)
            resource.to_array()
            self.assertEqual(resource._included_registry, {})

    def test_to_response_includes_included_member(self):
        with self.app.test_request_context('/?include=posts'):
            post = FakePost(10, 'Hello World')
            user = FakeUser(1, 'Rio', 'rio@example.com', posts=[post])
            response = UserResource(user).to_response()
            body = response.get_json()
            self.assertIn('included', body)
            self.assertEqual(len(body['included']), 1)
            self.assertEqual(response.headers['Content-Type'], 'application/vnd.api+json')


class JsonApiSparseFieldsetTest(UnitTestCase):

    def before_each(self):
        self.app = Flask(__name__)

    def test_sparse_fieldset_filters_attributes(self):
        with self.app.test_request_context('/?fields[users]=name'):
            user = FakeUser(1, 'Rio', 'rio@example.com')
            arr = UserResource(user).to_array()
            self.assertEqual(arr['attributes'], {'name': 'Rio'})

    def test_no_fieldset_returns_all_attributes(self):
        with self.app.test_request_context('/'):
            user = FakeUser(1, 'Rio', 'rio@example.com')
            arr = UserResource(user).to_array()
            self.assertEqual(set(arr['attributes'].keys()), {'name', 'email'})

    def test_fieldset_for_different_type_does_not_apply(self):
        with self.app.test_request_context('/?fields[posts]=title'):
            user = FakeUser(1, 'Rio', 'rio@example.com')
            arr = UserResource(user).to_array()
            self.assertEqual(set(arr['attributes'].keys()), {'name', 'email'})


class JsonApiResourceCollectionTest(UnitTestCase):

    def before_each(self):
        self.app = Flask(__name__)

    def test_collection_to_array_returns_list_of_resource_objects(self):
        with self.app.test_request_context('/'):
            users = [FakeUser(1, 'Rio', 'r@x.com'), FakeUser(2, 'Budi', 'b@x.com')]
            collection = JsonApiResourceCollection(users, UserResource)
            arr = collection.to_array()
            self.assertEqual(len(arr), 2)
            self.assertEqual(arr[0]['type'], 'users')

    def test_collection_merges_included_without_duplicates(self):
        with self.app.test_request_context('/?include=posts'):
            shared_post = FakePost(99, 'Shared Post')
            user1 = FakeUser(1, 'Rio', 'r@x.com', posts=[shared_post])
            user2 = FakeUser(2, 'Budi', 'b@x.com', posts=[shared_post])

            collection = JsonApiResourceCollection([user1, user2], UserResource)
            response = collection.to_response()
            body = response.get_json()

            self.assertEqual(len(body['data']), 2)
            self.assertEqual(len(body['included']), 1)

    def test_resource_class_via_classmethod_collection(self):
        with self.app.test_request_context('/'):
            posts = [FakePost(1, 'A'), FakePost(2, 'B')]
            collection = PostResource.collection(posts)
            self.assertIsInstance(collection, JsonApiResourceCollection)
            arr = collection.to_array()
            self.assertEqual(len(arr), 2)


class JsonApiResponseStructureTest(UnitTestCase):

    def before_each(self):
        self.app = Flask(__name__)

    def test_response_includes_meta_and_links_when_provided(self):
        with self.app.test_request_context('/'):
            user = FakeUser(1, 'Rio', 'rio@example.com')
            response = UserResource(user).to_response(
                meta={'request_id': 'abc'},
                links={'self': '/users/1'}
            )
            body = response.get_json()
            self.assertEqual(body['meta'], {'request_id': 'abc'})
            self.assertEqual(body['links'], {'self': '/users/1'})

    def test_response_status_code_is_configurable(self):
        with self.app.test_request_context('/'):
            user = FakeUser(1, 'Rio', 'rio@example.com')
            response = UserResource(user).to_response(status=201)
            self.assertEqual(response.status_code, 201)

    def test_callable_resource_returns_response(self):
        with self.app.test_request_context('/'):
            user = FakeUser(1, 'Rio', 'rio@example.com')
            response = UserResource(user)()
            self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
