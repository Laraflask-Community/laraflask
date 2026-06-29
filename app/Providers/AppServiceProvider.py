"""
App Service Provider
====================

Register and boot application-level services. This is the primary place
to bind classes into the service container and bootstrap application
services that need to run on every request.
"""

from laraflask.core.providers import ServiceProvider


class AppServiceProvider(ServiceProvider):
    """
    Register any application services.

    This provider is responsible for binding services into the container
    and bootstrapping application-wide functionality such as view composers,
    custom validation rules, and macros.
    """

    # -------------------------------------------------------------------------
    # Declarative Bindings
    # -------------------------------------------------------------------------
    # The `bindings` dict provides a declarative way to register bindings.
    # Keys are abstract names or interfaces, values are concrete implementations.
    # These are resolved fresh each time they are requested from the container.
    #
    # Example:
    #   bindings = {
    #       'app.Services.PaymentGateway.PaymentGatewayInterface':
    #           'app.Services.PaymentGateway.StripePaymentGateway',
    #       'app.Services.Mailer.MailerInterface':
    #           'app.Services.Mailer.SmtpMailer',
    #   }

    bindings = {}

    # -------------------------------------------------------------------------
    # Declarative Singletons
    # -------------------------------------------------------------------------
    # The `singletons` dict works like `bindings` but ensures only one instance
    # is created and shared across the entire application lifecycle.
    #
    # Example:
    #   singletons = {
    #       'app.Services.Cache.CacheManager':
    #           'app.Services.Cache.RedisCacheManager',
    #       'app.Services.Analytics.AnalyticsService':
    #           'app.Services.Analytics.MixpanelAnalyticsService',
    #   }

    singletons = {}

    def register(self):
        """
        Register bindings into the service container.

        This method is called before any other provider's boot() method,
        so you can depend on all bindings being available when boot() runs.
        Use this method for container bindings only - do not attempt to
        use any services here, as they may not yet be registered.
        """
        # -----------------------------------------------------------------
        # Singleton Bindings
        # -----------------------------------------------------------------
        # Use singleton when you need a single shared instance across the app.
        # Ideal for: caching services, connection pools, configuration managers.
        #
        # self.app.singleton('Analytics', lambda app: AnalyticsService(
        #     api_key=app.config.get('services.analytics.key'),
        #     environment=app.config.get('app.env'),
        # ))
        #
        # self.app.singleton('PaymentGateway', lambda app: StripeGateway(
        #     secret_key=app.config.get('services.stripe.secret'),
        # ))

        # -----------------------------------------------------------------
        # Interface-to-Implementation Bindings
        # -----------------------------------------------------------------
        # Use bind when you want a fresh instance each time a service is
        # resolved from the container. Good for: request-scoped services.
        #
        # self.app.bind('CartService', lambda app: CartService(
        #     user=app.make('auth').user(),
        #     gateway=app.make('PaymentGateway'),
        # ))
        #
        # self.app.bind('NotificationService', lambda app: NotificationService(
        #     mailer=app.make('Mailer'),
        #     sms=app.make('SmsGateway'),
        # ))

        # -----------------------------------------------------------------
        # Instance Bindings
        # -----------------------------------------------------------------
        # Use instance when you already have a constructed object to register.
        # Useful for: configuration objects, third-party SDK clients.
        #
        # self.app.instance('AppConfig', AppConfig(
        #     debug=self.app.config.get('app.debug'),
        #     timezone=self.app.config.get('app.timezone'),
        # ))

        # -----------------------------------------------------------------
        # Contextual Bindings
        # -----------------------------------------------------------------
        # Bind different implementations based on the consuming class.
        #
        # self.app.when('app.Controllers.PhotoController.PhotoController') \
        #     .needs('FileSystem') \
        #     .give(lambda app: LocalFileSystem(base_path='photos/'))
        #
        # self.app.when('app.Controllers.VideoController.VideoController') \
        #     .needs('FileSystem') \
        #     .give(lambda app: S3FileSystem(bucket='videos'))

        pass

    def boot(self):
        """
        Bootstrap any application services.

        This method is called after ALL service providers have been registered,
        meaning you can type-hint and resolve any service from the container.
        Use this for: event listeners, route model bindings, view composers,
        custom validators, macros, and other bootstrap logic.
        """
        # -----------------------------------------------------------------
        # View Composers
        # -----------------------------------------------------------------
        # Attach data to views every time they are rendered.
        #
        # from laraflask.view.view import View
        #
        # View.composer('layouts.app', lambda view: view.with_data({
        #     'app_name': self.app.config.get('app.name'),
        #     'current_user': self.app.make('auth').user(),
        # }))
        #
        # View.composer('partials.navigation', lambda view: view.with_data({
        #     'nav_items': self.app.make('NavigationService').items(),
        # }))

        # -----------------------------------------------------------------
        # Custom Validation Rules
        # -----------------------------------------------------------------
        # Register application-wide validation rules.
        #
        # from laraflask.validation.validator import Validator
        #
        # Validator.extend('phone', lambda attribute, value, parameters:
        #     bool(re.match(r'^\+?[1-9]\d{1,14}$', value)),
        #     'The :attribute must be a valid phone number.'
        # )
        #
        # Validator.extend('strong_password', lambda attribute, value, parameters:
        #     len(value) >= 8 and any(c.isupper() for c in value)
        #     and any(c.isdigit() for c in value),
        #     'The :attribute must be at least 8 characters with uppercase and digit.'
        # )

        # -----------------------------------------------------------------
        # Macros
        # -----------------------------------------------------------------
        # Extend framework classes with custom methods at runtime.
        #
        # from laraflask.http.response import Response
        #
        # Response.macro('api_success', lambda self, data, message='OK':
        #     self.json({'success': True, 'data': data, 'message': message})
        # )
        #
        # Response.macro('api_error', lambda self, message, code=400:
        #     self.json({'success': False, 'error': message}, status=code)
        # )

        # -----------------------------------------------------------------
        # Model Observers
        # -----------------------------------------------------------------
        # Register observers that listen to Eloquent model events.
        #
        # from app.Models.User import User
        # from app.Observers.UserObserver import UserObserver
        #
        # User.observe(UserObserver)

        pass
