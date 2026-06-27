"""
Create users table migration.
"""

from laraflask.orm.migration import Migration, Schema


class Migration_Users(Migration):

    def up(self):
        """Run the migration."""
        Schema.create('users', lambda table: [
            table.id(),
            table.string('name'),
            table.string('email').unique(),
            table.string('password'),
            table.string('role', 50).default('user').nullable(),
            table.string('api_key', 100).nullable(),
            table.string('remember_token', 100).nullable(),
            table.datetime('email_verified_at').nullable(),
            table.timestamps(),
            table.soft_deletes(),
        ])

    def down(self):
        """Reverse the migration."""
        Schema.drop_if_exists('users')
