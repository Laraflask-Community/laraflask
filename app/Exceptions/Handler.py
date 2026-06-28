"""
Laraflask Exception Handler
Converts exceptions into appropriate HTTP responses.
"""

from __future__ import annotations
import logging
import traceback
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from laraflask.core.application import Application

logger = logging.getLogger('laraflask')


class Handler:
    """
    Central exception handler.
    Register with the Flask app to intercept all unhandled exceptions.
    """

    def __init__(self, app: 'Application'):
        self._app = app
        self._dont_report = [
            # Add exception classes that should not be logged
        ]

    def register(self):
        """Register error handlers on the Flask app."""
        flask = self._app.get_flask()

        @flask.errorhandler(400)
        def bad_request(e):
            return self._json_or_html({'message': 'Bad Request'}, 400)

        @flask.errorhandler(401)
        def unauthorized(e):
            return self._json_or_html({'message': 'Unauthenticated.'}, 401)

        @flask.errorhandler(403)
        def forbidden(e):
            return self._json_or_html({'message': 'Forbidden.'}, 403)

        @flask.errorhandler(404)
        def not_found(e):
            return self._json_or_html({'message': 'Not Found.'}, 404)

        @flask.errorhandler(405)
        def method_not_allowed(e):
            return self._json_or_html({'message': 'Method Not Allowed.'}, 405)

        @flask.errorhandler(419)
        def csrf_mismatch(e):
            return self._json_or_html({'message': 'CSRF token mismatch.'}, 419)

        @flask.errorhandler(422)
        def unprocessable(e):
            return self._json_or_html({'message': 'Unprocessable Entity.'}, 422)

        @flask.errorhandler(429)
        def too_many_requests(e):
            return self._json_or_html({'message': 'Too Many Requests.'}, 429)

        @flask.errorhandler(500)
        def server_error(e):
            return self._handle_server_error(e)

        @flask.errorhandler(Exception)
        def handle_exception(e):
            return self._handle_exception(e)

    def _handle_exception(self, e: Exception):
        """Handle any unhandled exception."""
        from flask import jsonify, request, redirect, url_for
        from laraflask.core.exceptions import (
            ModelNotFoundException, AuthorizationException,
            AuthenticationException, ValidationException, HttpException,
        )

        if isinstance(e, ModelNotFoundException):
            return self._json_or_html({'message': str(e)}, 404)

        if isinstance(e, AuthorizationException):
            return self._json_or_html({'message': str(e)}, 403)

        if isinstance(e, AuthenticationException):
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'message': 'Unauthenticated.'}), 401
            try:
                return redirect(url_for('login'))
            except Exception:
                return jsonify({'message': 'Unauthenticated.'}), 401

        if isinstance(e, ValidationException):
            return jsonify({
                'success': False,
                'message': 'Validation failed.',
                'errors':  e.errors,
            }), 422

        if isinstance(e, HttpException):
            return self._json_or_html({'message': str(e)}, e.status_code)

        return self._handle_server_error(e)

    def _handle_server_error(self, e: Exception):
        """Handle 500-level errors."""
        debug = self._app._flask.config.get('DEBUG', False)

        if not self._should_skip_report(e):
            self.report(e)

        if debug:
            return self._debug_response(e)

        return self._json_or_html(
            {'message': 'Internal Server Error. We are working on it.'},
            500
        )

    def _debug_response(self, e: Exception):
        from flask import jsonify, request, Response
        tb = traceback.format_exc()
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'message':   str(e),
                'exception': type(e).__name__,
                'trace':     tb.splitlines(),
            }), 500

        html = f"""<!DOCTYPE html>
<html>
<head>
  <title>Laraflask — {type(e).__name__}</title>
  <style>
    body{{font-family:-apple-system,sans-serif;background:#1e1b4b;color:#e2e8f0;margin:0;padding:2rem}}
    .err-box{{background:#0f172a;border-left:4px solid #ef4444;border-radius:8px;padding:1.5rem;max-width:900px;margin:0 auto}}
    h1{{color:#ef4444;font-size:1.5rem;margin-bottom:.5rem}}
    .exc-type{{color:#94a3b8;font-size:.875rem;margin-bottom:1.5rem}}
    pre{{background:#1e1b4b;padding:1.25rem;border-radius:6px;font-size:.8125rem;overflow-x:auto;color:#a5b4fc;line-height:1.7}}
    .badge{{display:inline-block;background:#312e81;color:#a5b4fc;padding:.2rem .65rem;border-radius:20px;font-size:.75rem;margin-bottom:1rem}}
  </style>
</head>
<body>
  <div class="err-box">
    <span class="badge">⚠️ DEBUG MODE</span>
    <h1>{type(e).__name__}: {str(e)}</h1>
    <p class="exc-type">An unhandled exception occurred</p>
    <pre>{tb}</pre>
  </div>
</body>
</html>"""
        return Response(html, status=500, mimetype='text/html')

    def _json_or_html(self, data: dict, status: int):
        from flask import jsonify, request
        if (request.is_json
                or request.path.startswith('/api/')
                or 'application/json' in request.headers.get('Accept', '')):
            return jsonify({'success': False, **data}), status
        return jsonify({'success': False, **data}), status

    def report(self, e: Exception):
        """Log the exception."""
        logger.error(
            f"Exception [{type(e).__name__}]: {e}\n{traceback.format_exc()}"
        )

    def _should_skip_report(self, e: Exception) -> bool:
        for exc_type in self._dont_report:
            if isinstance(e, exc_type):
                return True
        return False

    def dont_report(self, *exception_classes) -> 'Handler':
        self._dont_report.extend(exception_classes)
        return self
