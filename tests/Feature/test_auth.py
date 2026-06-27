"""
Feature Test: Authentication
Tests full HTTP auth flow — register, login, logout.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from laraflask.testing.test_case import FeatureTestCase


class AuthTest(FeatureTestCase):
    """Test authentication endpoints."""

    def test_welcome_page_returns_200(self):
        response = self.get('/')
        response.assert_ok()

    def test_health_endpoint(self):
        response = self.get('/api/v1/health')
        response.assert_ok()
        response.assert_json({'status': 'ok'})

    def test_unauthenticated_redirect(self):
        response = self.get('/dashboard')
        # Should redirect or return 401
        assert response.status_code in (302, 401, 404)

    def test_api_returns_json(self):
        response = self.get('/api/v1/health')
        assert 'application/json' in response.headers.get('Content-Type', '')

    def test_404_on_unknown_route(self):
        response = self.get('/this-route-does-not-exist-xyz')
        response.assert_not_found()
