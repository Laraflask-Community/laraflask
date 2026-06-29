"""
Database Seeder — runs all seeders.
python artisan.py db:seed
"""

from laraflask.orm.seeder import Seeder
from database.seeders.UserSeeder import UserSeeder


class DatabaseSeeder(Seeder):
    """Master seeder — calls all individual seeders."""

    def run(self):
        print("Seeding database...")
        self.call(UserSeeder)
        print("Database seeding completed!")
