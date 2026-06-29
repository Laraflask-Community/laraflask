"""
Traits Package
==============

Reusable mixins and traits that can be composed into models,
controllers, or other classes to share behavior.

Example:
    class SoftDeletes:
        def delete(self):
            self.deleted_at = datetime.utcnow()
            self.save()

        def force_delete(self):
            super().delete()
"""
