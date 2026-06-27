"""
User Seeder — seed the users table with test data.
"""

from app.Models.User import User


class UserSeeder:
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
        print("  ✓ Admin user created: admin@laraflask.dev / password")

        # Create test users with Faker
        try:
            from faker import Faker
            fake = Faker()

            for _ in range(10):
                User.create(
                    name=fake.name(),
                    email=fake.unique.email(),
                    password='password',
                    role='user',
                )
            print(f"  ✓ Created 10 test users")

        except ImportError:
            print("  ℹ  Install faker for bulk seeding: pip install faker")
