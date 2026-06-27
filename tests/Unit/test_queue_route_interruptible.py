"""
Unit Test: Queue::route() & Interruptible
Tests centralized job routing (connection/queue registration) and the
Interruptible mixin's interaction with Worker signal handling.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import signal
import unittest
from unittest.mock import MagicMock
from laraflask.testing.test_case import UnitTestCase
from laraflask.queue.queue import Queue, Job, Interruptible, Worker, SyncDriver, QueueMessage


# ─── Fixtures ─────────────────────────────────────────────────────────────────

class PlainJob(Job):
    queue = 'default'


class RoutedJob(Job):
    queue = 'default'


class ExplicitQueueJob(Job):
    queue = 'default'

    def __init__(self):
        self.queue = 'custom'  # old-style explicit override


class CleanupJob(Job, Interruptible):
    def __init__(self):
        self.cleaned_up = False

    def handle(self):
        pass

    def interrupted(self, sig):
        self.cleaned_up = True


# ─── Queue.route() ────────────────────────────────────────────────────────────

class QueueRouteTest(UnitTestCase):

    def after_each(self):
        Queue._routes.clear()
        Queue._connections.clear()

    def test_route_registers_connection_and_queue(self):
        Queue.route(RoutedJob, connection='redis', queue='high')
        route = Queue.route_for(RoutedJob)
        self.assertEqual(route, {'connection': 'redis', 'queue': 'high'})

    def test_route_for_unregistered_job_returns_empty_dict(self):
        self.assertEqual(Queue.route_for(PlainJob), {})

    def test_route_can_set_only_connection(self):
        Queue.route(RoutedJob, connection='redis')
        self.assertEqual(Queue.route_for(RoutedJob), {'connection': 'redis'})

    def test_route_can_set_only_queue(self):
        Queue.route(RoutedJob, queue='low')
        self.assertEqual(Queue.route_for(RoutedJob), {'queue': 'low'})

    def test_dispatch_uses_routed_queue_when_not_overridden(self):
        Queue.route(RoutedJob, connection='redis', queue='high')
        mock_driver = MagicMock()
        mock_driver.push.return_value = 'job-id'
        Queue._connections['redis'] = mock_driver
        Queue._connections['sync'] = mock_driver
        Queue.configure(default='sync')

        Queue.dispatch(RoutedJob())

        args, kwargs = mock_driver.push.call_args
        self.assertEqual(args[1], 'high')

    def test_dispatch_keeps_explicit_instance_override(self):
        Queue.route(ExplicitQueueJob, connection='redis', queue='high')
        mock_driver = MagicMock()
        mock_driver.push.return_value = 'job-id'
        Queue._connections['redis'] = mock_driver
        Queue._connections['sync'] = mock_driver
        Queue.configure(default='sync')

        Queue.dispatch(ExplicitQueueJob())

        args, kwargs = mock_driver.push.call_args
        self.assertEqual(args[1], 'custom')

    def test_dispatch_without_route_uses_job_default_queue(self):
        mock_driver = MagicMock()
        mock_driver.push.return_value = 'job-id'
        Queue._connections['sync'] = mock_driver
        Queue.configure(default='sync')

        Queue.dispatch(PlainJob())

        args, kwargs = mock_driver.push.call_args
        self.assertEqual(args[1], 'default')


# ─── Interruptible ────────────────────────────────────────────────────────────

class InterruptibleTest(UnitTestCase):

    def test_default_interrupted_is_a_noop(self):
        class BareJob(Job, Interruptible):
            def handle(self): pass

        job = BareJob()
        # Should not raise even though it's not overridden.
        job.interrupted(signal.SIGTERM)

    def test_custom_interrupted_runs_cleanup(self):
        job = CleanupJob()
        job.interrupted(signal.SIGTERM)
        self.assertTrue(job.cleaned_up)


class WorkerSignalHandlingTest(UnitTestCase):

    def before_each(self):
        self.worker = Worker(SyncDriver(), queue='default')

    def test_signal_handler_calls_interrupted_on_running_interruptible_job(self):
        job = CleanupJob()
        self.worker._current_job = job
        self.worker._register_signal_handlers()

        os.kill(os.getpid(), signal.SIGTERM)

        self.assertTrue(job.cleaned_up)
        self.assertFalse(self.worker._running)
        self.assertEqual(self.worker._received_signal, signal.SIGTERM)

    def test_signal_handler_does_not_crash_for_non_interruptible_job(self):
        job = PlainJob()
        self.worker._current_job = job
        self.worker._register_signal_handlers()

        try:
            os.kill(os.getpid(), signal.SIGTERM)
        except Exception as e:
            self.fail(f"Signal handler raised unexpectedly: {e}")

        self.assertFalse(self.worker._running)

    def test_signal_handler_does_not_crash_with_no_current_job(self):
        self.worker._current_job = None
        self.worker._register_signal_handlers()

        os.kill(os.getpid(), signal.SIGTERM)

        self.assertFalse(self.worker._running)


if __name__ == '__main__':
    unittest.main()
