"""
User Seeder — seed the users table with test data.
"""

from laraflask.orm.seeder import Seeder
from app.Models.User import User
from database.factories.UserFactory import UserFactory


class UserSeeder(Seeder):
    """Seed the users table."""

    def run(self):
        # Create admin user
        User.first_or_create(
            search={'email': 'admin@laraflask.dev'},
            attributes={
                'name': 'Admin User',
                'password': 'password',
                'role': 'admin',
            }
        )
        print("  \u2713 Admin user created: admin@laraflask.dev / password")

        # Create test users using the factory system
        UserFactory().times(10).create()
        print("  \u2713 Created 10 test users")
