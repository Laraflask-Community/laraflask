"""
Routes Package - Laraflask
==========================

This package contains all route definitions for the application, organized
into three distinct files based on their purpose and lifecycle:

    web.py      Session-based routes for browser clients.
                These routes are assigned the 'web' middleware group which
                provides session state, CSRF protection, and cookie handling.

    api.py      Stateless API routes for programmatic clients.
                These routes are typically prefixed with /api and use token-based
                authentication (JWT, API keys). Responses are always JSON via
                ApiResponse.

    console.py  Scheduled tasks (cron-like) managed by the framework scheduler.
                Define recurring commands, jobs, and closures that run on a
                timed basis without an incoming HTTP request.

Route Registration
------------------
The framework's RouteServiceProvider loads each file and injects the global
`Route` object (for web.py and api.py) or `Schedule` object (for console.py)
automatically. You do NOT need to import these -- they are available as globals
at module execution time.
"""
