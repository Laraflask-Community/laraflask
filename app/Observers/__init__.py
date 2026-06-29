"""
Observers Package
=================

Model observers that hook into Eloquent model lifecycle events
(creating, created, updating, updated, deleting, deleted, etc.).

Example:
    class UserObserver:
        def creating(self, user):
            user.uuid = generate_uuid()

        def deleted(self, user):
            Storage.delete(user.avatar_path)
"""
