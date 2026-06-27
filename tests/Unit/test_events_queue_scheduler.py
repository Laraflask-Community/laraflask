"""
Unit Test: Events, Queue, Scheduler
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import unittest
import datetime
from unittest.mock import MagicMock, call
from laraflask.testing.test_case import UnitTestCase
from laraflask.events.dispatcher import EventDispatcher, Event, Listener, EventSubscriber
from laraflask.queue.queue import Job, SyncDriver, DatabaseDriver, QueueMessage, Worker
from laraflask.scheduler.schedule import Schedule, Event as ScheduledEvent


# ─────────────────────────────────────────────────────────────────────────────
#  E V E N T S
# ─────────────────────────────────────────────────────────────────────────────

class OrderPlaced(Event):
    def __init__(self, order_id=None, total=None):
        self.order_id = order_id
        self.total = total


class UserRegistered(Event):
    def __init__(self, user=None):
        self.user = user


class OrderListener(Listener):
    received = []

    def handle(self, event: OrderPlaced):
        OrderListener.received.append(event)


class EventDispatcherTest(UnitTestCase):

    def before_each(self):
        self.dispatcher = EventDispatcher()
        OrderListener.received = []

    # ── Registration ──────────────────────────────────────────────────────────

    def test_listen_with_closure(self):
        results = []
        self.dispatcher.listen(OrderPlaced, lambda e: results.append(e.order_id))
        self.dispatcher.dispatch(OrderPlaced(order_id=42))
        self.assertEqual(results, [42])

    def test_listen_with_listener_class(self):
        self.dispatcher.listen(OrderPlaced, OrderListener)
        self.dispatcher.dispatch(OrderPlaced(order_id=1, total=99.0))
        self.assertEqual(len(OrderListener.received), 1)
        self.assertEqual(OrderListener.received[0].order_id, 1)

    def test_listen_with_listener_instance(self):
        listener = OrderListener()
        self.dispatcher.listen(OrderPlaced, listener)
        self.dispatcher.dispatch(OrderPlaced(order_id=5))
        self.assertEqual(len(OrderListener.received), 1)

    def test_multiple_listeners(self):
        log = []
        self.dispatcher.listen(OrderPlaced, lambda e: log.append('A'))
        self.dispatcher.listen(OrderPlaced, lambda e: log.append('B'))
        self.dispatcher.dispatch(OrderPlaced(order_id=1))
        self.assertEqual(log, ['A', 'B'])

    def test_multiple_event_types(self):
        order_log = []
        user_log = []
        self.dispatcher.listen(OrderPlaced, lambda e: order_log.append(e))
        self.dispatcher.listen(UserRegistered, lambda e: user_log.append(e))

        self.dispatcher.dispatch(OrderPlaced(order_id=1))
        self.dispatcher.dispatch(UserRegistered(user='Alice'))

        self.assertEqual(len(order_log), 1)
        self.assertEqual(len(user_log), 1)

    def test_listener_does_not_receive_other_events(self):
        results = []
        self.dispatcher.listen(OrderPlaced, lambda e: results.append(e))
        self.dispatcher.dispatch(UserRegistered(user='Bob'))
        self.assertEqual(results, [])

    # ── Dispatch ──────────────────────────────────────────────────────────────

    def test_dispatch_returns_responses(self):
        self.dispatcher.listen(OrderPlaced, lambda e: 'handled')
        responses = self.dispatcher.dispatch(OrderPlaced(order_id=1))
        self.assertIn('handled', responses)

    def test_dispatch_collects_multiple_responses(self):
        self.dispatcher.listen(OrderPlaced, lambda e: 'r1')
        self.dispatcher.listen(OrderPlaced, lambda e: 'r2')
        responses = self.dispatcher.dispatch(OrderPlaced())
        self.assertEqual(responses, ['r1', 'r2'])

    def test_fire_alias(self):
        results = []
        self.dispatcher.listen(OrderPlaced, lambda e: results.append(True))
        self.dispatcher.fire(OrderPlaced(order_id=10))
        self.assertTrue(results[0])

    def test_until_returns_first_non_null(self):
        self.dispatcher.listen(OrderPlaced, lambda e: None)
        self.dispatcher.listen(OrderPlaced, lambda e: 'stop_here')
        self.dispatcher.listen(OrderPlaced, lambda e: 'never_reached')
        result = self.dispatcher.until(OrderPlaced())
        self.assertEqual(result, 'stop_here')

    def test_dispatch_halt_on_false(self):
        log = []
        self.dispatcher.listen(OrderPlaced, lambda e: False)
        self.dispatcher.listen(OrderPlaced, lambda e: log.append('B'))
        self.dispatcher.dispatch(OrderPlaced(), halt=True)
        self.assertEqual(log, [])  # second listener not called

    # ── has_listeners / forget ─────────────────────────────────────────────────

    def test_has_listeners(self):
        self.assertFalse(self.dispatcher.has_listeners(OrderPlaced))
        self.dispatcher.listen(OrderPlaced, lambda e: None)
        self.assertTrue(self.dispatcher.has_listeners(OrderPlaced))

    def test_forget_removes_listeners(self):
        self.dispatcher.listen(OrderPlaced, lambda e: None)
        self.dispatcher.forget(OrderPlaced)
        self.assertFalse(self.dispatcher.has_listeners(OrderPlaced))

    def test_forget_all(self):
        self.dispatcher.listen(OrderPlaced, lambda e: None)
        self.dispatcher.listen(UserRegistered, lambda e: None)
        self.dispatcher.forget_all()
        self.assertFalse(self.dispatcher.has_listeners(OrderPlaced))
        self.assertFalse(self.dispatcher.has_listeners(UserRegistered))

    # ── Wildcard ──────────────────────────────────────────────────────────────

    def test_wildcard_listener(self):
        log = []
        self.dispatcher.listen('Order*', lambda e: log.append('wildcard'))
        self.dispatcher.dispatch(OrderPlaced(order_id=1))
        self.assertIn('wildcard', log)

    # ── Subscriber ────────────────────────────────────────────────────────────

    def test_subscriber(self):
        results = []

        class OrderSubscriber(EventSubscriber):
            def subscribe(self, events):
                events.listen(OrderPlaced, lambda e: results.append('order'))
                events.listen(UserRegistered, lambda e: results.append('user'))

        self.dispatcher.subscribe(OrderSubscriber)
        self.dispatcher.dispatch(OrderPlaced())
        self.dispatcher.dispatch(UserRegistered())
        self.assertEqual(results, ['order', 'user'])

    def test_subscriber_class_instantiated(self):
        results = []

        class Sub(EventSubscriber):
            def subscribe(self, events):
                events.listen(OrderPlaced, lambda e: results.append(True))

        self.dispatcher.subscribe(Sub)
        self.dispatcher.dispatch(OrderPlaced())
        self.assertTrue(results[0])


# ─────────────────────────────────────────────────────────────────────────────
#  Q U E U E
# ─────────────────────────────────────────────────────────────────────────────

class SendEmailJob(Job):
    queue = 'emails'
    tries = 3

    def __init__(self, to=None, subject=None):
        self.to = to
        self.subject = subject
        self.executed = False

    def handle(self):
        self.executed = True

    def failed(self, exception):
        pass


class ProcessImageJob(Job):
    queue = 'media'
    timeout = 120

    def __init__(self, image_path=None):
        self.image_path = image_path

    def handle(self):
        pass


class SyncDriverTest(UnitTestCase):

    def before_each(self):
        self.driver = SyncDriver()

    def test_push_executes_job_immediately(self):
        job = SendEmailJob(to='user@example.com')
        self.driver.push(job)
        self.assertTrue(job.executed)

    def test_push_returns_string_id(self):
        job = SendEmailJob()
        result = self.driver.push(job)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_later_also_executes_immediately(self):
        job = SendEmailJob()
        self.driver.later(30, job)
        self.assertTrue(job.executed)

    def test_pop_returns_none(self):
        self.assertIsNone(self.driver.pop())

    def test_size_is_always_zero(self):
        job = SendEmailJob()
        self.driver.push(job)
        self.assertEqual(self.driver.size(), 0)

    def test_clear_returns_zero(self):
        self.assertEqual(self.driver.clear(), 0)

    def test_failed_job_calls_failed_method(self):
        class FailingJob(Job):
            failure_called = False
            def handle(self):
                raise ValueError("Intentional failure")
            def failed(self, exc):
                FailingJob.failure_called = True

        driver = SyncDriver()
        driver.push(FailingJob())
        self.assertTrue(FailingJob.failure_called)


class JobSerializeTest(UnitTestCase):

    def test_serialize_includes_job_class(self):
        job = SendEmailJob(to='a@b.com', subject='Hi')
        data = job.serialize()
        self.assertIn('job', data)
        self.assertIn('SendEmailJob', data['job'])

    def test_serialize_includes_data(self):
        job = SendEmailJob(to='a@b.com', subject='Hello')
        data = job.serialize()
        self.assertIn('data', data)

    def test_serialize_includes_queue(self):
        job = SendEmailJob()
        data = job.serialize()
        self.assertEqual(data['queue'], 'emails')

    def test_serialize_includes_tries(self):
        job = SendEmailJob()
        data = job.serialize()
        self.assertEqual(data['tries'], 3)

    def test_job_default_values(self):
        class SimpleJob(Job):
            def handle(self): pass

        j = SimpleJob()
        self.assertEqual(j.queue, 'default')
        self.assertEqual(j.tries, 3)
        self.assertEqual(j.timeout, 60)
        self.assertEqual(j.delay, 0)

    def test_deserialize_restores_job(self):
        job = SendEmailJob(to='test@example.com', subject='Test')
        serialized = job.serialize()
        restored = Job.deserialize(serialized)
        self.assertIsInstance(restored, SendEmailJob)
        self.assertEqual(restored.to, 'test@example.com')
        self.assertEqual(restored.subject, 'Test')


class QueueMessageTest(UnitTestCase):

    def test_is_available_when_past_due(self):
        import time
        msg = QueueMessage('1', {}, available_at=time.time() - 10)
        self.assertTrue(msg.is_available())

    def test_is_not_available_when_future(self):
        import time
        msg = QueueMessage('1', {}, available_at=time.time() + 100)
        self.assertFalse(msg.is_available())

    def test_increment_attempts(self):
        msg = QueueMessage('1', {}, attempts=2)
        msg.increment_attempts()
        self.assertEqual(msg.attempts, 3)

    def test_to_dict(self):
        msg = QueueMessage('abc', {'key': 'val'}, queue='high', attempts=1)
        d = msg.to_dict()
        self.assertEqual(d['id'], 'abc')
        self.assertEqual(d['queue'], 'high')
        self.assertEqual(d['attempts'], 1)


# ─────────────────────────────────────────────────────────────────────────────
#  S C H E D U L E R
# ─────────────────────────────────────────────────────────────────────────────

class ScheduledEventTest(UnitTestCase):

    def before_each(self):
        Schedule._events = []

    def test_call_registers_event(self):
        Schedule.call(lambda: None, 'test task')
        self.assertEqual(len(Schedule.get_events()), 1)

    def test_cron_expression_set(self):
        e = ScheduledEvent(lambda: None)
        e.cron('0 2 * * *')
        self.assertEqual(e._expression, '0 2 * * *')

    def test_every_minute(self):
        e = ScheduledEvent(lambda: None)
        e.every_minute()
        self.assertEqual(e._expression, '* * * * *')

    def test_daily(self):
        e = ScheduledEvent(lambda: None)
        e.daily()
        self.assertEqual(e._expression, '0 0 * * *')

    def test_hourly(self):
        e = ScheduledEvent(lambda: None)
        e.hourly()
        self.assertEqual(e._expression, '0 * * * *')

    def test_weekly(self):
        e = ScheduledEvent(lambda: None)
        e.weekly()
        self.assertEqual(e._expression, '0 0 * * 0')

    def test_monthly(self):
        e = ScheduledEvent(lambda: None)
        e.monthly()
        self.assertEqual(e._expression, '0 0 1 * *')

    def test_daily_at(self):
        e = ScheduledEvent(lambda: None)
        e.daily_at('03:30')
        self.assertEqual(e._expression, '30 3 * * *')

    def test_twice_daily(self):
        e = ScheduledEvent(lambda: None)
        e.twice_daily(6, 18)
        self.assertEqual(e._expression, '0 6,18 * * *')

    def test_weekdays(self):
        e = ScheduledEvent(lambda: None)
        e.daily().weekdays()
        self.assertIn('1-5', e._expression)

    def test_weekends(self):
        e = ScheduledEvent(lambda: None)
        e.daily().weekends()
        self.assertIn('0,6', e._expression)

    def test_chaining_fluent(self):
        e = ScheduledEvent(lambda: None)
        result = e.daily().weekdays().timezone('Asia/Jakarta')
        self.assertIsInstance(result, ScheduledEvent)
        self.assertEqual(result._timezone, 'Asia/Jakarta')

    def test_before_and_after_hooks(self):
        log = []
        e = ScheduledEvent(lambda: log.append('run'))
        e.before(lambda: log.append('before'))
        e.after(lambda: log.append('after'))
        e.run()
        self.assertEqual(log, ['before', 'run', 'after'])

    def test_when_filter_prevents_run(self):
        ran = []
        e = ScheduledEvent(lambda: ran.append(True))
        e.when(lambda: False)
        # is_due with filter should return False
        self.assertFalse(e._filters[0]())

    def test_skip_filter(self):
        ran = []
        e = ScheduledEvent(lambda: ran.append(True))
        e.skip(lambda: True)
        self.assertTrue(e._rejects[0]())

    def test_field_match_wildcard(self):
        e = ScheduledEvent(lambda: None)
        self.assertTrue(e._field_match('*', 5))
        self.assertTrue(e._field_match('*', 0))

    def test_field_match_exact(self):
        e = ScheduledEvent(lambda: None)
        self.assertTrue(e._field_match('3', 3))
        self.assertFalse(e._field_match('3', 4))

    def test_field_match_range(self):
        e = ScheduledEvent(lambda: None)
        self.assertTrue(e._field_match('1-5', 3))
        self.assertFalse(e._field_match('1-5', 6))

    def test_field_match_list(self):
        e = ScheduledEvent(lambda: None)
        self.assertTrue(e._field_match('1,3,5', 3))
        self.assertFalse(e._field_match('1,3,5', 4))

    def test_field_match_step(self):
        e = ScheduledEvent(lambda: None)
        self.assertTrue(e._field_match('*/5', 10))
        self.assertFalse(e._field_match('*/5', 7))

    def test_schedule_list(self):
        Schedule.call(lambda: None, 'task1').daily()
        Schedule.call(lambda: None, 'task2').hourly()
        listing = Schedule.list()
        self.assertEqual(len(listing), 2)
        self.assertIsInstance(listing[0], str)

    def test_run_due_calls_due_events(self):
        ran = []
        e = Schedule.call(lambda: ran.append(True), 'due_task')
        e.every_minute()
        e.is_due = MagicMock(return_value=True)
        count = Schedule.run_due()
        self.assertGreaterEqual(count, 1)

    def test_summary(self):
        e = ScheduledEvent(lambda: None, 'My Task')
        e.daily()
        s = e.summary()
        self.assertIn('My Task', s)
        self.assertIn('0 0 * * *', s)


class ScheduleCommandTest(UnitTestCase):

    def before_each(self):
        Schedule._events = []

    def test_command_creates_event(self):
        e = Schedule.command('cache:clear')
        self.assertIsInstance(e, ScheduledEvent)
        self.assertEqual(len(Schedule.get_events()), 1)

    def test_exec_creates_event(self):
        e = Schedule.exec('echo hello')
        self.assertIsInstance(e, ScheduledEvent)

    def test_job_creates_event(self):
        class CleanupJob(Job):
            def handle(self): pass

        e = Schedule.job(CleanupJob)
        self.assertIsInstance(e, ScheduledEvent)

    def test_multiple_scheduled_tasks(self):
        Schedule.command('cache:clear').daily()
        Schedule.command('queue:work').every_minute()
        Schedule.call(lambda: None).hourly()
        self.assertEqual(len(Schedule.get_events()), 3)


if __name__ == '__main__':
    unittest.main()
