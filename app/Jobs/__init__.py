"""
Jobs Package
============

Queueable background jobs for asynchronous processing.
Jobs implement a handle() method and can be dispatched to the queue.

Example:
    class ProcessPayment:
        def handle(self):
            ...

    # Dispatch:
    Queue.push(ProcessPayment(order_id=123))
"""
