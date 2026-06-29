"""
Notifications Package
=====================

Notification classes for sending messages to users via multiple channels
(mail, database, broadcast, SMS, etc.).

Example:
    class InvoicePaid:
        def via(self, notifiable):
            return ['mail', 'database']

        def to_mail(self, notifiable):
            return MailMessage().subject('Invoice Paid').line('...')
"""
