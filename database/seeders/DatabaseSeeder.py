"""
Database Seeder — runs all seeders.
python artisan.py db:seed
"""

from database.seeders.UserSeeder import UserSeeder


class DatabaseSeeder:
    """Master seeder — calls all individual seeders."""

    def run(self):
        print("Seeding database...")
        UserSeeder().run()
        print("Database seeding completed!")
