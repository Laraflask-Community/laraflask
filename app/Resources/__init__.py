"""
Resources Package
=================

API resource classes that transform models into JSON-serializable
representations for API responses.

Example:
    class UserResource:
        def to_array(self, model):
            return {
                'id':    model.id,
                'name':  model.name,
                'email': model.email,
            }
"""
