"""
Model Concerns (Mixins/Traits)

Reusable behavior mixins following the Laravel Concerns pattern.
Import and mix into any Model class.
"""
from app.Models.Concerns.HasRoles import HasRoles

__all__ = ['HasRoles']
