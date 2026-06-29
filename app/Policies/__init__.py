"""
Policies Package
================

Authorization policies that determine if a user can perform actions
on a given model. Policies are registered in AuthServiceProvider.

Example:
    class PostPolicy:
        def update(self, user, post):
            return user.id == post.user_id

        def delete(self, user, post):
            return user.id == post.user_id or user.is_admin()
"""
