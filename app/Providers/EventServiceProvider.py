"""
Event Service Provider
======================

Register application events and their corresponding listeners.
Events provide a simple observer pattern implementation, allowing you
to decouple various aspects of your application.
"""

from laraflask.core.providers import ServiceProvider


class EventServiceProvider(ServiceProvider):
    """
    Register event listeners and subscribers.

    The `listen` property maps event classes to an array of listener classes.
    When the event is dispatched, each listener's handle() method is called
    in the order they are listed.

    The `subscribe` property lists event subscriber classes. Subscribers
    define their own `subscribe()` method which manually registers listeners
    for multiple events, providing a convenient way to group related handlers.
    """

    # -------------------------------------------------------------------------
    # Event-to-Listener Mappings
    # -------------------------------------------------------------------------
    # Each key is an event class and each value is a list of listener classes
    # that should be invoked when that event fires.
    #
    # Example:
    #   from app.Events.UserRegistered import UserRegistered
    #   from app.Events.OrderPlaced import OrderPlaced
    #   from app.Events.PaymentProcessed import PaymentProcessed
    #   from app.Listeners.SendWelcomeEmail import SendWelcomeEmail
    #   from app.Listeners.CreateUserProfile import CreateUserProfile
    #   from app.Listeners.AssignDefaultRole import AssignDefaultRole
    #   from app.Listeners.SendOrderConfirmation import SendOrderConfirmation
    #   from app.Listeners.DecreaseInventory import DecreaseInventory
    #   from app.Listeners.NotifyWarehouse import NotifyWarehouse
    #   from app.Listeners.SendPaymentReceipt import SendPaymentReceipt
    #   from app.Listeners.UpdateAccountBalance import UpdateAccountBalance

    listen = {
        # UserRegistered: [
        #     SendWelcomeEmail,
        #     CreateUserProfile,
        #     AssignDefaultRole,
        # ],
        # OrderPlaced: [
        #     SendOrderConfirmation,
        #     DecreaseInventory,
        #     NotifyWarehouse,
        # ],
        # PaymentProcessed: [
        #     SendPaymentReceipt,
        #     UpdateAccountBalance,
        # ],
    }

    # -------------------------------------------------------------------------
    # Event Subscribers
    # -------------------------------------------------------------------------
    # Subscribers handle multiple events in a single class. The subscriber
    # class defines a subscribe() method that receives the event dispatcher
    # and can register multiple listeners manually.
    #
    # Example:
    #   from app.Listeners.OrderEventSubscriber import OrderEventSubscriber
    #   from app.Listeners.UserActivitySubscriber import UserActivitySubscriber

    subscribe = [
        # OrderEventSubscriber,
        # UserActivitySubscriber,
    ]

    def register(self):
        """Register any event-related services."""
        pass

    def boot(self):
        """Register all event listeners and subscribers with the dispatcher."""
        from laraflask.events.dispatcher import Events

        # Register all event-listener mappings
        for event_class, listeners in self.listen.items():
            for listener_class in listeners:
                Events.listen(event_class, listener_class)

        # Register event subscribers
        for subscriber_class in self.subscribe:
            Events.subscribe(subscriber_class)

    def should_discover_events(self):
        """
        Determine if events and listeners should be automatically discovered.

        When enabled, the framework will scan the app/Events/ and
        app/Listeners/ directories to automatically register event-listener
        pairs based on type hints in the listener's handle() method.

        Auto-discovery eliminates the need to manually register events in the
        `listen` dict above, but adds a small performance overhead on boot.
        In production, discovered events are cached.

        Returns:
            bool: True to enable auto-discovery, False to use manual registration.
        """
        return False
