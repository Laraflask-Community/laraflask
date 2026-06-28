"""
User Model
"""

import laraflask
from laraflask.orm.model import Model
from laraflask.auth.auth import Hash
from laraflask.notifications.notification import Notifiable


class User(Model, Notifiable):
    """
    User model — the default authentication model.
    """

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

    # ─── Custom Methods ───────────────────────────────────────────────────────

    def is_admin(self) -> bool:
        return self._attributes.get('role') == 'admin'

    def has_verified_email(self) -> bool:
        return self._attributes.get('email_verified_at') is not None

    @classmethod
    def find_by_email(cls, email: str):
        return cls.where('email', email).first()

    def generate_api_key(self) -> str:
        import secrets
        key = secrets.token_hex(40)
        self._attributes['api_key'] = key
        self.save()
        return key
