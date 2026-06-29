"""
Database Factories Package
==========================

Factories generate fake model instances for testing and seeding.
Each factory defines a definition() method returning default attributes.
"""

from database.factories.UserFactory import Factory, UserFactory

__all__ = ["Factory", "UserFactory"]
