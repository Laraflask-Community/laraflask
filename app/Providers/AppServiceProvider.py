"""
App Service Provider
Register and boot application-level services.
"""

from laraflask.core.providers import ServiceProvider


class AppServiceProvider(ServiceProvider):
    """
    Register any application services.
    """

    def register(self):
        """Register bindings into the container."""
        # self.app.bind('MyService', MyService)
        # self.app.singleton('Analytics', AnalyticsService)
        pass

    def boot(self):
        """Bootstrap any application services."""
        # Register view composers
        # Register macros
        # Load translations
        pass
