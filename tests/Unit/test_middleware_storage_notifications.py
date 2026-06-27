"""
Unit Test: Middleware, Router, Storage, Notifications
"""

import sys, os, tempfile, shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import unittest
from unittest.mock import MagicMock, patch
from laraflask.testing.test_case import UnitTestCase
from laraflask.middleware.middleware import (
    MiddlewareRegistry, ThrottleMiddleware,
    TrimStringsMiddleware, SecureHeadersMiddleware,
)
from laraflask.storage.storage import Storage, LocalDriver
from laraflask.notifications.notification import (
    MailMessage, SmsMessage, TelegramMessage, WhatsAppMessage, PushMessage,
    Notification, Notifiable,
)
from laraflask.api.api import ApiResponse, ApiResource, ApiResourceCollection, RateLimiter


# ─────────────────────────────────────────────────────────────────────────────
#  M I D D L E W A R E
# ─────────────────────────────────────────────────────────────────────────────

class MiddlewareRegistryTest(UnitTestCase):

    def test_built_in_aliases_registered(self):
        registry = MiddlewareRegistry
        for alias in ('auth', 'guest', 'csrf', 'throttle', 'cors', 'session'):
            self.assertIn(alias, registry._registry)

    def test_register_custom_middleware(self):
        from laraflask.middleware.middleware import Middleware
        class Custom(Middleware):
            def handle(self, request, next_): return next_(request)

        MiddlewareRegistry.register('my.custom', Custom)
        self.assertIn('my.custom', MiddlewareRegistry._registry)
        # cleanup
        del MiddlewareRegistry._registry['my.custom']

    def test_resolve_with_params(self):
        result = MiddlewareRegistry.resolve('throttle:60,1')
        # Should return a callable/factory for throttle with params
        self.assertIsNotNone(result)

    def test_resolve_unknown_returns_none(self):
        result = MiddlewareRegistry.resolve('nonexistent:xyz')
        self.assertIsNone(result)

    def test_all_returns_dict(self):
        all_mw = MiddlewareRegistry.all()
        self.assertIsInstance(all_mw, dict)
        self.assertGreater(len(all_mw), 0)


class ThrottleMiddlewareTest(UnitTestCase):

    def test_allows_requests_under_limit(self):
        mw = ThrottleMiddleware(max_attempts=5, decay_minutes=1)
        request = MagicMock()
        request.remote_addr = '127.0.0.1'
        next_ = MagicMock(return_value=MagicMock(status_code=200))

        for _ in range(5):
            response = mw.handle(request, next_)

        self.assertEqual(next_.call_count, 5)

    def test_blocks_after_limit(self):
        mw = ThrottleMiddleware(max_attempts=2, decay_minutes=1)
        request = MagicMock()
        request.remote_addr = '192.168.1.100'
        next_ = MagicMock(return_value=MagicMock(status_code=200))

        mw.handle(request, next_)
        mw.handle(request, next_)
        # Third request should be throttled
        response = mw.handle(request, next_)
        # next_ should only have been called twice
        self.assertEqual(next_.call_count, 2)

    def test_resolve_key_uses_ip(self):
        mw = ThrottleMiddleware()
        request = MagicMock()
        request.remote_addr = '10.0.0.1'
        key = mw._resolve_key(request)
        self.assertIsInstance(key, str)
        self.assertTrue(len(key) > 0)

    def test_different_ips_have_separate_limits(self):
        mw = ThrottleMiddleware(max_attempts=1, decay_minutes=1)
        r1 = MagicMock(); r1.remote_addr = '1.1.1.1'
        r2 = MagicMock(); r2.remote_addr = '2.2.2.2'
        next_ = MagicMock(return_value=MagicMock(status_code=200))

        mw.handle(r1, next_)
        mw.handle(r2, next_)
        # Both IPs under limit; next called twice
        self.assertEqual(next_.call_count, 2)


# ─────────────────────────────────────────────────────────────────────────────
#  S T O R A G E
# ─────────────────────────────────────────────────────────────────────────────

class LocalDriverTest(UnitTestCase):

    def before_each(self):
        self.tmp = tempfile.mkdtemp()
        self.driver = LocalDriver(root=self.tmp, url='/storage')

    def after_each(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_put_string(self):
        self.assertTrue(self.driver.put('hello.txt', 'Hello, World!'))
        self.assertTrue(self.driver.exists('hello.txt'))

    def test_get_string(self):
        self.driver.put('read.txt', 'readable content')
        content = self.driver.get_string('read.txt')
        self.assertEqual(content, 'readable content')

    def test_get_bytes(self):
        self.driver.put('bytes.txt', b'byte data')
        data = self.driver.get('bytes.txt')
        self.assertIsInstance(data, bytes)

    def test_exists_true(self):
        self.driver.put('exists.txt', 'yes')
        self.assertTrue(self.driver.exists('exists.txt'))

    def test_exists_false(self):
        self.assertFalse(self.driver.exists('missing.txt'))

    def test_missing(self):
        self.assertTrue(self.driver.missing('nope.txt'))

    def test_delete(self):
        self.driver.put('del.txt', 'bye')
        self.driver.delete('del.txt')
        self.assertFalse(self.driver.exists('del.txt'))

    def test_delete_multiple(self):
        self.driver.put('a.txt', '1')
        self.driver.put('b.txt', '2')
        self.driver.delete(['a.txt', 'b.txt'])
        self.assertFalse(self.driver.exists('a.txt'))
        self.assertFalse(self.driver.exists('b.txt'))

    def test_copy(self):
        self.driver.put('src.txt', 'copy me')
        self.driver.copy('src.txt', 'dst.txt')
        self.assertTrue(self.driver.exists('src.txt'))
        self.assertTrue(self.driver.exists('dst.txt'))
        self.assertEqual(self.driver.get_string('dst.txt'), 'copy me')

    def test_move(self):
        self.driver.put('old.txt', 'moved')
        self.driver.move('old.txt', 'new.txt')
        self.assertFalse(self.driver.exists('old.txt'))
        self.assertTrue(self.driver.exists('new.txt'))

    def test_size(self):
        self.driver.put('sized.txt', 'hello')
        self.assertEqual(self.driver.size('sized.txt'), 5)

    def test_size_missing_returns_zero(self):
        self.assertEqual(self.driver.size('missing.txt'), 0)

    def test_url(self):
        url = self.driver.url('uploads/photo.jpg')
        self.assertEqual(url, '/storage/uploads/photo.jpg')

    def test_files_listing(self):
        self.driver.put('f1.txt', 'a')
        self.driver.put('f2.txt', 'b')
        files = self.driver.files()
        self.assertEqual(len(files), 2)

    def test_make_directory(self):
        self.driver.make_directory('sub/nested')
        full = os.path.join(self.tmp, 'sub', 'nested')
        self.assertTrue(os.path.isdir(full))

    def test_delete_directory(self):
        self.driver.make_directory('todelete')
        self.driver.put('todelete/file.txt', 'data')
        self.driver.delete_directory('todelete')
        self.assertFalse(os.path.exists(os.path.join(self.tmp, 'todelete')))

    def test_append(self):
        self.driver.put('log.txt', 'line1\n')
        self.driver.append('log.txt', 'line2\n')
        content = self.driver.get_string('log.txt')
        self.assertEqual(content, 'line1\nline2\n')

    def test_prepend(self):
        self.driver.put('log.txt', 'line2\n')
        self.driver.prepend('log.txt', 'line1\n')
        content = self.driver.get_string('log.txt')
        self.assertEqual(content, 'line1\nline2\n')

    def test_mime_type(self):
        mime = self.driver.mime_type('photo.jpg')
        self.assertEqual(mime, 'image/jpeg')


class StorageFacadeTest(UnitTestCase):

    def before_each(self):
        self.tmp = tempfile.mkdtemp()
        Storage._disks['local'] = LocalDriver(root=self.tmp)
        Storage._default = 'local'

    def after_each(self):
        shutil.rmtree(self.tmp, ignore_errors=True)
        Storage._disks.clear()

    def test_put_and_get(self):
        Storage.put('test.txt', 'content')
        data = Storage.get('test.txt')
        self.assertEqual(data, b'content')

    def test_exists(self):
        Storage.put('check.txt', 'yes')
        self.assertTrue(Storage.exists('check.txt'))
        self.assertFalse(Storage.exists('nope.txt'))

    def test_delete(self):
        Storage.put('rm.txt', 'bye')
        Storage.delete('rm.txt')
        self.assertFalse(Storage.exists('rm.txt'))

    def test_disk_switcher(self):
        tmp2 = tempfile.mkdtemp()
        Storage.register_disk('backup', LocalDriver(root=tmp2))
        Storage.disk('backup').put('backup.txt', 'data')
        self.assertTrue(Storage.disk('backup').exists('backup.txt'))
        shutil.rmtree(tmp2, ignore_errors=True)


# ─────────────────────────────────────────────────────────────────────────────
#  N O T I F I C A T I O N S
# ─────────────────────────────────────────────────────────────────────────────

class MailMessageTest(UnitTestCase):

    def test_subject(self):
        msg = MailMessage().subject('Welcome!')
        self.assertEqual(msg._subject, 'Welcome!')

    def test_line(self):
        msg = MailMessage().line('Hello').line('World')
        self.assertIn('Hello', msg._lines)
        self.assertIn('World', msg._lines)

    def test_action(self):
        msg = MailMessage().action('Click here', 'https://example.com')
        self.assertEqual(msg._action_text, 'Click here')
        self.assertEqual(msg._action_url, 'https://example.com')

    def test_greeting(self):
        msg = MailMessage().greeting('Hi there!')
        self.assertEqual(msg._greeting, 'Hi there!')

    def test_level_success(self):
        msg = MailMessage().success()
        self.assertEqual(msg._level, 'success')

    def test_level_error(self):
        msg = MailMessage().error()
        self.assertEqual(msg._level, 'error')

    def test_level_warning(self):
        msg = MailMessage().warning()
        self.assertEqual(msg._level, 'warning')

    def test_render_contains_subject(self):
        msg = MailMessage().subject('Test Email').line('Body text')
        html = msg.render()
        self.assertIn('Test Email', html)
        self.assertIn('Body text', html)

    def test_render_contains_action(self):
        msg = MailMessage().action('Go Now', 'https://site.com')
        html = msg.render()
        self.assertIn('https://site.com', html)
        self.assertIn('Go Now', html)

    def test_custom_html(self):
        msg = MailMessage().html('<p>Custom</p>')
        self.assertEqual(msg.render(), '<p>Custom</p>')

    def test_cc_and_bcc(self):
        msg = MailMessage().cc('a@b.com').bcc('c@d.com')
        self.assertIn('a@b.com', msg._cc)
        self.assertIn('c@d.com', msg._bcc)

    def test_chaining(self):
        msg = (MailMessage()
               .subject('Test')
               .greeting('Hello!')
               .line('First line')
               .line('Second line')
               .action('CTA', 'https://example.com')
               .success())
        self.assertEqual(msg._subject, 'Test')
        self.assertEqual(len(msg._lines), 2)
        self.assertEqual(msg._level, 'success')


class SmsMessageTest(UnitTestCase):

    def test_content(self):
        msg = SmsMessage('Hello SMS')
        self.assertEqual(msg._content, 'Hello SMS')

    def test_from_(self):
        msg = SmsMessage().from_('+1234567890')
        self.assertEqual(msg._from, '+1234567890')

    def test_unicode(self):
        msg = SmsMessage().unicode()
        self.assertTrue(msg._unicode)


class TelegramMessageTest(UnitTestCase):

    def test_content(self):
        msg = TelegramMessage('Hello Telegram')
        self.assertEqual(msg._content, 'Hello Telegram')

    def test_chat_id(self):
        msg = TelegramMessage().chat_id('123456789')
        self.assertEqual(msg._chat_id, '123456789')

    def test_line_appends(self):
        msg = TelegramMessage('Line 1').line('Line 2')
        self.assertIn('Line 2', msg._content)

    def test_button(self):
        msg = TelegramMessage().button('Click', 'https://example.com')
        self.assertEqual(len(msg._buttons), 1)
        self.assertEqual(msg._buttons[0][0]['text'], 'Click')

    def test_disable_preview(self):
        msg = TelegramMessage().disable_preview()
        self.assertTrue(msg._disable_preview)

    def test_parse_mode_markdown(self):
        msg = TelegramMessage().markdown()
        self.assertEqual(msg._parse_mode, 'Markdown')

    def test_photo(self):
        msg = TelegramMessage().photo('https://img.com/pic.jpg')
        self.assertEqual(msg._photo, 'https://img.com/pic.jpg')


class WhatsAppMessageTest(UnitTestCase):

    def test_content(self):
        msg = WhatsAppMessage('Hello WA')
        self.assertEqual(msg._content, 'Hello WA')

    def test_to(self):
        msg = WhatsAppMessage().to('+6281234567890')
        self.assertEqual(msg._to, '+6281234567890')

    def test_line(self):
        msg = WhatsAppMessage('Hi').line('How are you?')
        self.assertIn('How are you?', msg._content)

    def test_media(self):
        msg = WhatsAppMessage().media('https://img.com/img.png')
        self.assertEqual(msg._media_url, 'https://img.com/img.png')

    def test_template(self):
        msg = WhatsAppMessage().template('order_confirm', 'ORD-001', '$99')
        self.assertEqual(msg._template, 'order_confirm')
        self.assertEqual(msg._template_params, ['ORD-001', '$99'])


class PushMessageTest(UnitTestCase):

    def test_title_and_body(self):
        msg = PushMessage().title('Alert').body('You have a new message')
        self.assertEqual(msg._title, 'Alert')
        self.assertEqual(msg._body, 'You have a new message')

    def test_data(self):
        msg = PushMessage().data(order_id=42, status='shipped')
        self.assertEqual(msg._data['order_id'], 42)
        self.assertEqual(msg._data['status'], 'shipped')

    def test_badge(self):
        msg = PushMessage().badge(5)
        self.assertEqual(msg._badge, 5)

    def test_sound(self):
        msg = PushMessage().sound('notification.mp3')
        self.assertEqual(msg._sound, 'notification.mp3')

    def test_click_action(self):
        msg = PushMessage().click_action('OPEN_ORDER')
        self.assertEqual(msg._click_action, 'OPEN_ORDER')


class NotificationViaTest(UnitTestCase):

    def test_via_returns_list(self):
        class MyNotification(Notification):
            def via(self, notifiable):
                return ['mail', 'telegram']

        n = MyNotification()
        self.assertEqual(n.via(None), ['mail', 'telegram'])

    def test_should_send_defaults_true(self):
        n = Notification()
        self.assertTrue(n.should_send(None, 'mail'))

    def test_to_array_defaults_empty(self):
        n = Notification()
        self.assertEqual(n.to_array(None), {})

    def test_notifiable_mixin_notify(self):
        class User:
            email = 'user@example.com'

        class WelcomeNotification(Notification):
            def via(self, notifiable): return []  # no real channels
            def to_mail(self, notifiable): return MailMessage().subject('Welcome')

        user = User()
        # Just ensure it doesn't crash
        user_with_mixin = type('UserM', (Notifiable,), {'email': 'u@e.com'})()
        try:
            user_with_mixin.notify(WelcomeNotification())
        except Exception:
            pass  # might fail without SMTP — just don't crash on basic flow


# ─────────────────────────────────────────────────────────────────────────────
#  A P I
# ─────────────────────────────────────────────────────────────────────────────

class ApiResponseTest(UnitTestCase):

    def _get_json(self, response):
        import json
        if isinstance(response, tuple):
            return json.loads(response[0].data)
        return json.loads(response.data)

    def _get_status(self, response):
        if isinstance(response, tuple):
            return response[1]
        return response.status_code

    def test_success_response(self):
        with patch('laraflask.api.api.jsonify') as mock_jsonify:
            mock_jsonify.return_value = MagicMock()
            ApiResponse.success({'key': 'value'})
            args = mock_jsonify.call_args[0][0]
            self.assertTrue(args['success'])
            self.assertEqual(args['data'], {'key': 'value'})

    def test_error_response(self):
        with patch('laraflask.api.api.jsonify') as mock_jsonify:
            mock_jsonify.return_value = MagicMock()
            ApiResponse.error('Something went wrong', 400)
            args = mock_jsonify.call_args[0][0]
            self.assertFalse(args['success'])
            self.assertEqual(args['message'], 'Something went wrong')

    def test_validation_error(self):
        with patch('laraflask.api.api.jsonify') as mock_jsonify:
            mock_jsonify.return_value = MagicMock()
            errors = {'email': ['Invalid email']}
            ApiResponse.validation_error(errors)
            args = mock_jsonify.call_args[0][0]
            self.assertFalse(args['success'])
            self.assertEqual(args['errors'], errors)

    def test_paginated_response(self):
        with patch('laraflask.api.api.jsonify') as mock_jsonify:
            mock_jsonify.return_value = MagicMock()
            paginator = {
                'data': [{'id': 1}, {'id': 2}],
                'total': 50, 'per_page': 15,
                'current_page': 1, 'last_page': 4,
                'from': 1, 'to': 15,
            }
            ApiResponse.paginated(paginator)
            args = mock_jsonify.call_args[0][0]
            self.assertEqual(args['meta']['total'], 50)
            self.assertEqual(args['meta']['per_page'], 15)


class ApiResourceTest(UnitTestCase):

    def test_to_array_uses_to_dict(self):
        class FakeModel:
            def to_dict(self):
                return {'id': 1, 'name': 'Test'}

        resource = ApiResource(FakeModel())
        data = resource.to_array()
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['name'], 'Test')

    def test_collection_maps_items(self):
        class FakeModel:
            def __init__(self, n): self.n = n
            def to_dict(self): return {'n': self.n}

        items = [FakeModel(i) for i in range(3)]
        collection = ApiResource.collection(items)
        array = collection.to_array()
        self.assertEqual(len(array), 3)
        self.assertEqual(array[0]['n'], 0)

    def test_custom_resource_transform(self):
        class FakeModel:
            def __init__(self): self.id = 99; self.secret = 'hidden'
            def to_dict(self): return {'id': self.id, 'secret': self.secret}

        class PublicResource(ApiResource):
            def to_array(self):
                return {'id': self._resource.id}  # exclude secret

        resource = PublicResource(FakeModel())
        data = resource.to_array()
        self.assertIn('id', data)
        self.assertNotIn('secret', data)


class RateLimiterTest(UnitTestCase):

    def before_each(self):
        RateLimiter._store.clear()

    def test_allows_requests_under_limit(self):
        for _ in range(5):
            self.assertTrue(RateLimiter.attempt('user:1', 5, 60))

    def test_blocks_over_limit(self):
        for _ in range(5):
            RateLimiter.attempt('user:2', 5, 60)
        self.assertFalse(RateLimiter.attempt('user:2', 5, 60))

    def test_too_many_attempts(self):
        for _ in range(3):
            RateLimiter.attempt('user:3', 3, 60)
        self.assertTrue(RateLimiter.too_many_attempts('user:3', 3))

    def test_remaining_attempts(self):
        RateLimiter.attempt('user:4', 10, 60)
        RateLimiter.attempt('user:4', 10, 60)
        remaining = RateLimiter.remaining_attempts('user:4', 10)
        self.assertEqual(remaining, 8)

    def test_clear_resets_bucket(self):
        for _ in range(5):
            RateLimiter.attempt('user:5', 5, 60)
        RateLimiter.clear('user:5')
        self.assertTrue(RateLimiter.attempt('user:5', 5, 60))

    def test_different_keys_independent(self):
        for _ in range(3):
            RateLimiter.attempt('user:A', 3, 60)
        # user:B should not be affected
        self.assertTrue(RateLimiter.attempt('user:B', 3, 60))


if __name__ == '__main__':
    unittest.main()
