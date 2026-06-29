"""
Requests Package
================

Form request classes that encapsulate validation rules and authorization
logic for incoming HTTP requests.

Example:
    class StorePostRequest:
        def rules(self):
            return {
                'title': 'required|string|max:255',
                'body':  'required|string',
            }

        def authorize(self):
            return self.user() is not None
"""
