"""
Middleware Package
==================

HTTP middleware that filters requests before they reach controllers.
Middleware can inspect, modify, or reject requests and responses.

Example:
    class Authenticate:
        def handle(self, request, next):
            if not Auth.check():
                return redirect('/login')
            return next(request)
"""
