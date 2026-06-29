"""
User Model
"""

from __future__ import annotations

__all__ = ['User']

import laraflask
from laraflask.orm.model import Model
from laraflask.auth.auth import Hash
from laraflask.notifications.notification import Notifiable
from app.Models.Concerns.HasRoles import HasRoles


class User(Model, Notifiable, HasRoles):
    """
    User model -- the default authentication model.

    Inherits role-management helpers from HasRoles and notification
    support from Notifiable.
    """

    # ─── Role Constants ───────────────────────────────────────────────────────

    ROLE_ADMIN: str = 'admin'
    ROLE_USER: str = 'user'

    # ─── Table & Mass-Assignment ──────────────────────────────────────────────

    __table__    = 'users'
    __fillable__ = ['name', 'email', 'password']
    __hidden__   = ['password', 'remember_token']
    __casts__    = {
        'email_verified_at': 'datetime',
        'created_at':        'datetime',
        'updated_at':        'datetime',
    }

    # ─── Mutators ─────────────────────────────────────────────────────────────

    def set_password_attribute(self, value: str) -> str:
        """Auto-hash passwords on assignment."""
        if value and not value.startswith('$2b$') and not value.startswith('sha256$'):
            return Hash.make(value)
        return value

    # ─── Accessors ────────────────────────────────────────────────────────────

    def get_gravatar_url_attribute(self) -> str:
        """Get Gravatar URL based on email."""
        import hashlib
        email_hash = hashlib.md5(
            self._attributes.get('email', '').lower().encode()
        ).hexdigest()
        return f"https://www.gravatar.com/avatar/{email_hash}?s=200&d=mp"

    # ─── Relationships ────────────────────────────────────────────────────────

    # @property
    # def posts(self):
    #     from app.Models.Post import Post
    #     return self.has_many(Post)

    # @property
    # def profile(self):
    #     from app.Models.Profile import Profile
    #     return self.has_one(Profile)

    # ─── Query Scopes ─────────────────────────────────────────────────────────
    # Uncomment and implement when the ORM supports scope methods.

    # @classmethod
    # def admins(cls):
    #     """Scope: only users with the admin role."""
    #     return cls.where('role', cls.ROLE_ADMIN)

    # @classmethod
    # def verified(cls):
    #     """Scope: only users who have verified their email."""
    #     return cls.where_not_null('email_verified_at')

    # @classmethod
    # def active(cls):
    #     """Scope: only active (non-banned) users."""
    #     return cls.where('is_active', True)

    # ─── Custom Methods ───────────────────────────────────────────────────────

    def is_admin(self) -> bool:
        """Check whether the user has the admin role."""
        return self._attributes.get('role') == self.ROLE_ADMIN

    def has_verified_email(self) -> bool:
        """Check whether the user has verified their email address."""
        return self._attributes.get('email_verified_at') is not None

    @classmethod
    def find_by_email(cls, email: str):
        """Find a user by their email address."""
        return cls.where('email', email).first()

    def generate_api_key(self) -> str:
        """Generate and persist a new API key for the user."""
        import secrets
        key: str = secrets.token_hex(40)
        self._attributes['api_key'] = key
        self.save()
        return key
