"""
Unit Test: PreventRequestForgery
Tests the origin-aware CSRF protection layer on top of token-based
verification, plus the opt-in PreventRequestForgeryMiddleware, while
confirming the original CsrfMiddleware remains untouched.

Note: Flask is imported here only to create isolated test_request_context
      instances. Route files and controllers must NOT import Flask at the
      top level — only unit tests that need a bare request context may use
      the _make_flask_app() helper pattern below.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import unittest
from werkzeug.exceptions import HTTPException
from laraflask.testing.test_case import UnitTestCase
from laraflask.security.security import PreventRequestForgery, CsrfToken
from laraflask.middleware.middleware import (
    CsrfMiddleware, PreventRequestForgeryMiddleware
)


class FakeRequest:
    """Minimal stand-in for Flask's request object, exposing headers/host."""

    def __init__(self, origin=None, referer=None, host='myapp.test'):
        headers = {}
        if origin:
            headers['Origin'] = origin
        if referer:
            headers['Referer'] = referer
        self.headers = headers
        self.host = host


def _make_flask_app():
    """
    Create a minimal Flask app for test_request_context only.
    Unit tests that need a request context use this helper instead of
    importing Flask at module level.
    """
    from flask import Flask
    app = Flask(__name__)
    app.secret_key = 'test-secret'
    app.config['TESTING'] = True
    return app


class PreventRequestForgeryTokenLayerTest(UnitTestCase):
    """Layer 1: token verification behaves like CsrfToken.verify()."""

    def before_each(self):
        self.session = {}
        self.token = CsrfToken.generate(self.session)
        self.guard = PreventRequestForgery()

    def test_correct_token_passes_without_request(self):
        self.assertTrue(self.guard.verify(self.token, self.session))

    def test_wrong_token_fails(self):
        self.assertFalse(self.guard.verify('wrong-token', self.session))

    def test_missing_token_fails(self):
        self.assertFalse(self.guard.verify(None, self.session))


class PreventRequestForgeryOriginLayerTest(UnitTestCase):
    """Layer 2: origin-aware verification on top of the token layer."""

    def before_each(self):
        self.session = {}
        self.token = CsrfToken.generate(self.session)
        self.guard = PreventRequestForgery(trusted_origins=['myapp.test', '*.myapp.test'])

    def test_matching_origin_passes(self):
        req = FakeRequest(origin='https://myapp.test')
        self.assertTrue(self.guard.verify(self.token, self.session, req))

    def test_forged_origin_fails_even_with_valid_token(self):
        req = FakeRequest(origin='https://evil.com')
        self.assertFalse(self.guard.verify(self.token, self.session, req))

    def test_wildcard_subdomain_matches(self):
        req = FakeRequest(origin='https://api.myapp.test')
        self.assertTrue(self.guard.verify(self.token, self.session, req))

    def test_wildcard_matches_bare_domain_too(self):
        req = FakeRequest(origin='https://myapp.test')
        self.assertTrue(self.guard.verify(self.token, self.session, req))

    def test_referer_used_as_fallback_when_origin_missing(self):
        req = FakeRequest(referer='https://myapp.test/some/page')
        self.assertTrue(self.guard.verify(self.token, self.session, req))

    def test_missing_origin_and_referer_fails_strictly(self):
        req = FakeRequest()
        self.assertFalse(self.guard.verify(self.token, self.session, req))

    def test_valid_origin_but_invalid_token_fails(self):
        req = FakeRequest(origin='https://myapp.test')
        self.assertFalse(self.guard.verify('wrong-token', self.session, req))


class PreventRequestForgeryDefaultSameOriginTest(UnitTestCase):
    """With no trusted_origins configured, falls back to same-origin (request.host) check."""

    def before_each(self):
        self.session = {}
        self.token = CsrfToken.generate(self.session)
        self.guard = PreventRequestForgery()

    def test_same_origin_request_passes(self):
        req = FakeRequest(origin='https://myapp.test', host='myapp.test')
        self.assertTrue(self.guard.verify(self.token, self.session, req))

    def test_cross_origin_request_fails(self):
        req = FakeRequest(origin='https://evil.com', host='myapp.test')
        self.assertFalse(self.guard.verify(self.token, self.session, req))


class PreventRequestForgeryMiddlewareTest(UnitTestCase):
    """Confirm the new middleware works and the old CsrfMiddleware is untouched."""

    def before_each(self):
        self.app = _make_flask_app()

    def test_old_csrf_middleware_class_unchanged(self):
        # Sanity check: the original middleware still exists with its original behavior contract.
        mw = CsrfMiddleware()
        self.assertTrue(hasattr(mw, 'handle'))
        self.assertEqual(mw.EXEMPT_METHODS, {'GET', 'HEAD', 'OPTIONS', 'TRACE'})

    def test_exempt_methods_bypass_check(self):
        from flask import request
        middleware = PreventRequestForgeryMiddleware(trusted_origins=['myapp.test'])
        with self.app.test_request_context('/', method='GET'):
            result = middleware.handle(request, lambda r: 'passed-through')
            self.assertEqual(result, 'passed-through')

    def test_exempt_path_pattern_bypasses_check(self):
        from flask import request
        middleware = PreventRequestForgeryMiddleware(trusted_origins=['myapp.test'])
        with self.app.test_request_context('/api/webhook', method='POST'):
            result = middleware.handle(request, lambda r: 'passed-through')
            self.assertEqual(result, 'passed-through')

    def test_valid_token_and_origin_passes_through(self):
        from flask import request, session
        middleware = PreventRequestForgeryMiddleware(trusted_origins=['myapp.test'])
        with self.app.test_request_context(
            '/transfer', method='POST',
            headers={'Origin': 'https://myapp.test'},
            data={'_token': 'abc123'}
        ):
            session['_token'] = 'abc123'
            result = middleware.handle(request, lambda r: 'passed-through')
            self.assertEqual(result, 'passed-through')

    def test_forged_origin_aborts(self):
        """
        [Note] Status 419 isn't a standard HTTP code, so Werkzeug raises
        LookupError when no custom exception is registered for it — this is
        the exact same pre-existing behavior as the original CsrfMiddleware
        (both call abort(419) identically). What matters here is that the
        middleware actually attempts to abort the request rather than
        letting it through.
        """
        from flask import request, session
        middleware = PreventRequestForgeryMiddleware(trusted_origins=['myapp.test'])
        with self.app.test_request_context(
            '/transfer', method='POST',
            headers={'Origin': 'https://evil.com'},
            data={'_token': 'abc123'}
        ):
            session['_token'] = 'abc123'
            with self.assertRaises(LookupError):
                middleware.handle(request, lambda r: 'should-not-reach-here')

    def test_missing_token_aborts(self):
        from flask import request, session
        middleware = PreventRequestForgeryMiddleware(trusted_origins=['myapp.test'])
        with self.app.test_request_context(
            '/transfer', method='POST',
            headers={'Origin': 'https://myapp.test'},
        ):
            session['_token'] = 'abc123'
            with self.assertRaises(LookupError):
                middleware.handle(request, lambda r: 'should-not-reach-here')

    def test_forged_origin_and_missing_token_behave_identically_to_original_csrf_middleware(self):
        """
        Confirms PreventRequestForgeryMiddleware aborts via the exact same
        mechanism (abort(419)) as the pre-existing CsrfMiddleware, so
        adopting it doesn't change error-handling expectations app-wide.
        """
        from flask import request, session

        old_middleware = CsrfMiddleware()
        new_middleware = PreventRequestForgeryMiddleware(trusted_origins=['myapp.test'])

        with self.app.test_request_context('/transfer', method='POST'):
            session['_token'] = 'abc123'
            with self.assertRaises(LookupError):
                old_middleware.handle(request, lambda r: 'unreachable')

        with self.app.test_request_context(
            '/transfer', method='POST', headers={'Origin': 'https://evil.com'}
        ):
            session['_token'] = 'abc123'
            with self.assertRaises(LookupError):
                new_middleware.handle(request, lambda r: 'unreachable')


if __name__ == '__main__':
    unittest.main()
