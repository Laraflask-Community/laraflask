"""
Event Service Provider
Register events and their listeners.
"""

from laraflask.core.providers import ServiceProvider


class EventServiceProvider(ServiceProvider):
    """
    Register event listeners and subscribers.

    Listen format:
        listen = {
            EventClass: [Listener1, Listener2],
        }
    """

    listen = {
        # UserRegistered: [
        #     SendWelcomeEmailListener,
        #     CreateUserProfileListener,
        # ],
        # OrderPlaced: [
        #     SendOrderConfirmationListener,
        #     DecreaseInventoryListener,
        # ],
    }

    subscribe = [
        # OrderEventSubscriber,
    ]

    def register(self):
        pass

    def boot(self):
        """Register all listeners and subscribers."""
        from laraflask.events.dispatcher import Events

        for event_class, listeners in self.listen.items():
            for listener_class in listeners:
                Events.listen(event_class, listener_class)

        for subscriber_class in self.subscribe:
            Events.subscribe(subscriber_class)
