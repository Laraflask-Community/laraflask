"""
Exceptions Package
==================

Application exception handler and custom exception classes.
The Handler class converts exceptions into appropriate HTTP responses.
"""

from app.Exceptions.Handler import Handler

__all__ = ["Handler"]
