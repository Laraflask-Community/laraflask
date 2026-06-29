"""
Database Factories Package
==========================

Factories generate fake model instances for testing and seeding.
Each factory defines a definition() method returning default attributes.

The base Factory class is provided by the laraflask-core framework.
"""

from database.factories.UserFactory import UserFactory

__all__ = ["UserFactory"]
