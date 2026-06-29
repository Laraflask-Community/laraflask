"""
Rules Package
=============

Custom validation rules that extend the framework's built-in validators.

Example:
    class Uppercase:
        def passes(self, attribute, value):
            return value == value.upper()

        def message(self):
            return 'The :attribute must be uppercase.'
"""
