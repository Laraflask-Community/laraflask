"""
Models Package
==============

Eloquent-style ORM models representing database tables.

Subpackages:
    Concerns - Reusable model mixins (HasRoles, etc.)
"""

from app.Models.User import User

__all__ = ["User"]
