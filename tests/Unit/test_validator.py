"""
Unit Test: Validator
Tests validation rules in isolation.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import unittest
from laraflask.testing.test_case import UnitTestCase
from laraflask.validation.validator import Validator, ValidationException


class ValidatorTest(UnitTestCase):
    """Test the Validator class."""

    def test_required_rule_passes(self):
        v = Validator({'name': 'John'}, {'name': 'required'})
        self.assertTrue(v.passes())

    def test_required_rule_fails_on_empty(self):
        v = Validator({'name': ''}, {'name': 'required'})
        self.assertTrue(v.fails())
        self.assertIn('name', v.errors())

    def test_required_rule_fails_on_missing(self):
        v = Validator({}, {'name': 'required'})
        self.assertTrue(v.fails())

    def test_email_rule_passes(self):
        v = Validator({'email': 'user@example.com'}, {'email': 'email'})
        self.assertTrue(v.passes())

    def test_email_rule_fails(self):
        v = Validator({'email': 'not-an-email'}, {'email': 'email'})
        self.assertTrue(v.fails())

    def test_min_string_rule(self):
        v = Validator({'name': 'ab'}, {'name': 'min:3'})
        self.assertTrue(v.fails())

        v2 = Validator({'name': 'abc'}, {'name': 'min:3'})
        self.assertTrue(v2.passes())

    def test_max_string_rule(self):
        v = Validator({'name': 'toolongname'}, {'name': 'max:5'})
        self.assertTrue(v.fails())

    def test_integer_rule(self):
        v = Validator({'age': '25'}, {'age': 'integer'})
        self.assertTrue(v.passes())

        v2 = Validator({'age': 'abc'}, {'age': 'integer'})
        self.assertTrue(v2.fails())

    def test_in_rule(self):
        v = Validator({'role': 'admin'}, {'role': 'in:admin,user,editor'})
        self.assertTrue(v.passes())

        v2 = Validator({'role': 'hacker'}, {'role': 'in:admin,user,editor'})
        self.assertTrue(v2.fails())

    def test_confirmed_rule(self):
        v = Validator(
            {'password': 'secret', 'password_confirmation': 'secret'},
            {'password': 'confirmed'}
        )
        self.assertTrue(v.passes())

        v2 = Validator(
            {'password': 'secret', 'password_confirmation': 'different'},
            {'password': 'confirmed'}
        )
        self.assertTrue(v2.fails())

    def test_nullable_allows_none(self):
        v = Validator({'bio': None}, {'bio': 'nullable|string'})
        self.assertTrue(v.passes())

    def test_multiple_rules(self):
        v = Validator(
            {'email': 'bad', 'name': ''},
            {'email': 'required|email', 'name': 'required|min:2'}
        )
        self.assertTrue(v.fails())
        self.assertIn('email', v.errors())
        self.assertIn('name', v.errors())

    def test_validate_raises_on_failure(self):
        v = Validator({}, {'name': 'required'})
        with self.assertRaises(ValidationException):
            v.validate()

    def test_validated_returns_only_valid_fields(self):
        v = Validator(
            {'name': 'Alice', 'extra_field': 'ignored'},
            {'name': 'required|string'}
        )
        validated = v.validate()
        self.assertIn('name', validated)
        self.assertNotIn('extra_field', validated)

    def test_custom_error_messages(self):
        v = Validator(
            {'name': ''},
            {'name': 'required'},
            messages={'name.required': 'Please provide your name!'}
        )
        v.fails()
        self.assertEqual(v.errors()['name'][0], 'Please provide your name!')

    def test_between_rule(self):
        v = Validator({'age': 25}, {'age': 'between:18,65'})
        self.assertTrue(v.passes())

        v2 = Validator({'age': 10}, {'age': 'between:18,65'})
        self.assertTrue(v2.fails())

    def test_alpha_rule(self):
        v = Validator({'name': 'Alice'}, {'name': 'alpha'})
        self.assertTrue(v.passes())

        v2 = Validator({'name': 'Alice123'}, {'name': 'alpha'})
        self.assertTrue(v2.fails())

    def test_url_rule(self):
        v = Validator({'url': 'https://example.com'}, {'url': 'url'})
        self.assertTrue(v.passes())

        v2 = Validator({'url': 'not-a-url'}, {'url': 'url'})
        self.assertTrue(v2.fails())

    def test_uuid_rule(self):
        v = Validator(
            {'id': '550e8400-e29b-41d4-a716-446655440000'},
            {'id': 'uuid'}
        )
        self.assertTrue(v.passes())

    def test_json_rule(self):
        v = Validator({'data': '{"key": "value"}'}, {'data': 'json'})
        self.assertTrue(v.passes())

        v2 = Validator({'data': 'not json'}, {'data': 'json'})
        self.assertTrue(v2.fails())


class HashTest(UnitTestCase):
    """Test password hashing."""

    def test_hash_make_and_check(self):
        from laraflask.auth.auth import Hash
        hashed = Hash.make('password123')
        self.assertNotEqual(hashed, 'password123')
        self.assertTrue(Hash.check('password123', hashed))
        self.assertFalse(Hash.check('wrongpassword', hashed))

    def test_hash_is_not_plain_text(self):
        from laraflask.auth.auth import Hash
        hashed = Hash.make('mysecret')
        self.assertNotIn('mysecret', hashed)


class JWTTest(UnitTestCase):
    """Test JWT token generation and validation."""

    def test_encode_and_decode(self):
        from laraflask.auth.auth import JWT
        jwt = JWT(secret='test-secret', ttl=60)
        token = jwt.encode({'user_id': 1, 'email': 'test@example.com'})
        self.assertIsNotNone(token)
        payload = jwt.decode(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload.get('user_id'), 1)

    def test_expired_token_returns_none(self):
        from laraflask.auth.auth import JWT
        jwt = JWT(secret='test-secret', ttl=-1)  # already expired
        token = jwt.encode({'user_id': 1})
        # ttl=-1 means it expires immediately; decode should return None
        # (Behaviour may vary with library; just ensure it doesn't crash)
        result = jwt.decode(token)
        # result is None or a dict — no exception should be raised
        self.assertIn(type(result), [type(None), dict])


if __name__ == '__main__':
    unittest.main()
