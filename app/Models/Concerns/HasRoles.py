"""
HasRoles Concern (Mixin)

Provides role-checking and role-assignment behavior for any model
that stores a 'role' attribute. Mix into a Model subclass to gain
convenient role helpers.

Usage:
    class User(Model, HasRoles):
        ...
"""

from __future__ import annotations


class HasRoles:
    """
    Mixin that adds role management methods to a Model.

    Expects the consuming class to store attributes in ``self._attributes``
    (the standard Laraflask ORM attribute dict).
    """

    # ─── Role Constants ───────────────────────────────────────────────────────

    ROLE_ADMIN: str = 'admin'
    ROLE_USER: str = 'user'
    ROLE_MODERATOR: str = 'moderator'

    # ─── Role Query Methods ───────────────────────────────────────────────────

    def is_admin(self) -> bool:
        """Check whether the model instance has the admin role."""
        return self._attributes.get('role') == self.ROLE_ADMIN

    def is_moderator(self) -> bool:
        """Check whether the model instance has the moderator role."""
        return self._attributes.get('role') == self.ROLE_MODERATOR

    def has_role(self, role: str) -> bool:
        """
        Check whether the model instance has the given role.

        Args:
            role: The role string to check against.

        Returns:
            True if the instance's role matches the given role.
        """
        return self._attributes.get('role') == role

    # ─── Role Mutation Methods ────────────────────────────────────────────────

    def assign_role(self, role: str) -> None:
        """
        Assign a role to the model instance.

        Args:
            role: The role string to assign.
        """
        self._attributes['role'] = role

    def get_role(self) -> str:
        """
        Get the current role of the model instance.

        Returns:
            The role string, or an empty string if no role is set.
        """
        return self._attributes.get('role', '')
