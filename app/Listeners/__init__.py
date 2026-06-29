"""
Listeners Package
=================

Event listeners that react to dispatched events. Each listener
implements a handle() method that receives the event instance.

Example:
    class SendWelcomeEmail:
        def handle(self, event):
            Mail.to(event.user.email).send(WelcomeMail(event.user))
"""
