"""
Laraflask Factory System
Generate test data using Faker. Integrates with database seeders.
"""

from __future__ import annotations
import random
from typing import Any, Callable, Dict, List, Optional, Type


class Factory:
    """
    Model factory for generating test data.

    Usage:
        class UserFactory(Factory):
            model = User

            def definition(self) -> dict:
                return {
                    'name':     self.faker.name(),
                    'email':    self.faker.unique.email(),
                    'password': 'password',
                }

        # Create 10 users
        UserFactory.times(10).create()

        # Create with overrides
        UserFactory.create(role='admin')

        # Make without saving
        user = UserFactory.make(name='Alice')
    """

    model = None  # Set in subclass

    def __init__(self):
        try:
            from faker import Faker
            self.faker = Faker()
        except ImportError:
            self.faker = _FakerStub()

        self._count = 1
        self._states: List[str] = []
        self._overrides: Dict = {}
        self._after_making: List[Callable] = []
        self._after_creating: List[Callable] = []

    def definition(self) -> Dict:
        """Override to define the default attribute set."""
        return {}

    def _get_attributes(self, overrides: Dict = None) -> Dict:
        """Merge definition with any state overrides and explicit overrides."""
        attrs = self.definition()

        for state in self._states:
            state_method = f"state_{state}"
            if hasattr(self, state_method):
                attrs.update(getattr(self, state_method)())

        attrs.update(self._overrides)
        if overrides:
            attrs.update(overrides)

        return attrs

    # ─── Fluent Interface ─────────────────────────────────────────────────────

    def times(self, count: int) -> 'Factory':
        self._count = count
        return self

    def state(self, *states: str) -> 'Factory':
        self._states.extend(states)
        return self

    def after_making(self, callback: Callable) -> 'Factory':
        self._after_making.append(callback)
        return self

    def after_creating(self, callback: Callable) -> 'Factory':
        self._after_creating.append(callback)
        return self

    # ─── Create / Make ────────────────────────────────────────────────────────

    def make(self, **overrides) -> Any:
        """Build model instance(s) without persisting."""
        results = []
        for _ in range(self._count):
            attrs = self._get_attributes(overrides)
            instance = self.model(**attrs)
            for cb in self._after_making:
                cb(instance)
            results.append(instance)

        return results[0] if self._count == 1 else results

    def create(self, **overrides) -> Any:
        """Create and persist model instance(s)."""
        results = []
        for _ in range(self._count):
            attrs = self._get_attributes(overrides)
            instance = self.model.create(**attrs)
            for cb in self._after_creating:
                cb(instance)
            results.append(instance)

        return results[0] if self._count == 1 else results

    def raw(self, **overrides) -> Any:
        """Return raw attribute dict(s) without creating a model."""
        if self._count == 1:
            return self._get_attributes(overrides)
        return [self._get_attributes(overrides) for _ in range(self._count)]

    # ─── Class-level shortcuts ────────────────────────────────────────────────

    @classmethod
    def _instance(cls) -> 'Factory':
        return cls()

    @classmethod
    def new(cls, **overrides) -> Any:
        return cls._instance().make(**overrides)

    @classmethod
    def new_many(cls, count: int, **overrides) -> List:
        return cls._instance().times(count).make(**overrides)

    @classmethod
    def persist(cls, **overrides) -> Any:
        return cls._instance().create(**overrides)

    @classmethod
    def persist_many(cls, count: int, **overrides) -> List:
        return cls._instance().times(count).create(**overrides)


class _FakerStub:
    """Minimal stub if Faker is not installed."""

    def __getattr__(self, name):
        return lambda *a, **kw: f"fake_{name}"

    @property
    def unique(self):
        return self


# ─── UserFactory example ─────────────────────────────────────────────────────

class UserFactory(Factory):
    """Default User factory."""

    @property
    def model(self):
        from app.Models.User import User
        return User

    def definition(self) -> Dict:
        return {
            'name':     self.faker.name(),
            'email':    self.faker.unique.email(),
            'password': 'password',
            'role':     'user',
        }

    def state_admin(self) -> Dict:
        return {'role': 'admin'}

    def state_verified(self) -> Dict:
        import datetime
        return {'email_verified_at': datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None).isoformat()}

    def state_unverified(self) -> Dict:
        return {'email_verified_at': None}
