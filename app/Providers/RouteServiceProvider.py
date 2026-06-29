"""
Route Service Provider
======================

Configure and load application route files. This provider gives you a
central place to control how routes are loaded, apply route-level
middleware groups, and define URI prefixes for different route contexts.

Note: The Laraflask framework automatically loads routes from the
routes/ directory. This provider is available for advanced customization
when you need fine-grained control over route loading order, middleware
assignment, or conditional route registration.
"""

from laraflask.core.providers import ServiceProvider


class RouteServiceProvider(ServiceProvider):
    """
    Configure route loading for the application.

    This provider allows you to customize how route files are loaded,
    including setting prefixes, middleware groups, and namespaces.
    By default, the framework handles route loading automatically,
    so this provider is only needed for advanced use cases.
    """

    # -------------------------------------------------------------------------
    # Constants
    # -------------------------------------------------------------------------

    # The path users are redirected to after login (used by auth middleware)
    HOME = '/dashboard'

    # The global rate limit for API routes (requests per minute)
    API_RATE_LIMIT = 60

    # The prefix applied to all API routes
    API_PREFIX = 'api'

    def register(self):
        """Register any route-related services."""
        pass

    def boot(self):
        """
        Define the route model bindings, pattern filters, and route loading.

        This method is called after all providers are registered. Use it to
        define route patterns, model bindings, and load route files with
        specific middleware/prefix configurations.
        """
        # -----------------------------------------------------------------
        # Route Pattern Constraints
        # -----------------------------------------------------------------
        # Define global patterns that apply to all route parameters.
        #
        # from laraflask.routing.route import Route
        #
        # Route.pattern('id', r'[0-9]+')
        # Route.pattern('slug', r'[a-z0-9\-]+')
        # Route.pattern('uuid', r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')

        # -----------------------------------------------------------------
        # Route Model Bindings
        # -----------------------------------------------------------------
        # Automatically resolve model instances from route parameters.
        #
        # from laraflask.routing.route import Route
        # from app.Models.User import User
        #
        # Route.model('user', User)
        # Route.bind('post', lambda value: Post.where('slug', value).first_or_fail())

        # -----------------------------------------------------------------
        # Route Loading
        # -----------------------------------------------------------------
        # The framework loads routes automatically from routes/web.py,
        # routes/api.py, and routes/console.py. The methods below show how
        # to customize route loading if you need different middleware groups
        # or additional route files.
        #
        # self.map_web_routes()
        # self.map_api_routes()
        # self.map_admin_routes()

        pass

    def map_web_routes(self):
        """
        Define the "web" routes for the application.

        These routes are assigned the "web" middleware group which includes
        session state, CSRF protection, and cookie encryption.
        """
        # from laraflask.routing.route import Route
        #
        # Route.middleware(['web']).group(lambda: (
        #     __import__('importlib').import_module('routes.web'),
        # ))
        pass

    def map_api_routes(self):
        """
        Define the "api" routes for the application.

        These routes are assigned the "api" middleware group which includes
        rate limiting and stateless authentication (token/key based).
        Routes are automatically prefixed with /api.
        """
        # from laraflask.routing.route import Route
        #
        # Route.prefix(self.API_PREFIX) \
        #     .middleware(['api', f'throttle:{self.API_RATE_LIMIT},1']) \
        #     .group(lambda: (
        #         __import__('importlib').import_module('routes.api'),
        #     ))
        pass

    def map_admin_routes(self):
        """
        Define the "admin" routes for the application.

        Example of adding a custom route group for an admin panel with
        its own prefix, middleware stack, and route file.
        """
        # from laraflask.routing.route import Route
        #
        # Route.prefix('admin') \
        #     .middleware(['web', 'auth', 'admin']) \
        #     .group(lambda: (
        #         __import__('importlib').import_module('routes.admin'),
        #     ))
        pass
