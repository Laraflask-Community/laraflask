"""
User Factory — generates fake User model instances for testing and seeding.

Usage:
    from database.factories.UserFactory import UserFactory

    # Create 10 users
    UserFactory().times(10).create()

    # Create with overrides
    UserFactory().create(role='admin')

    # Make without saving
    user = UserFactory().make(name='Alice')

    # Use states
    UserFactory().state('admin').create()
"""

from __future__ import annotations
from typing import Dict

from laraflask.orm.factory import Factory


class UserFactory(Factory):
    """Default User factory."""

    @property
    def model(self):
        from app.Models.User import User
        return User

    def definition(self) -> Dict:
        return {
            'name': self.faker.name(),
            'email': self.faker.unique.email(),
            'password': 'password',
            'role': 'user',
        }

    def state_admin(self) -> Dict:
        return {'role': 'admin'}

    def state_verified(self) -> Dict:
        import datetime
        return {'email_verified_at': datetime.datetime.utcnow().isoformat()}

    def state_unverified(self) -> Dict:
        return {'email_verified_at': None}
