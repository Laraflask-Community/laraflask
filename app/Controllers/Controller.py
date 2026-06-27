"""
Laraflask Base Controller
All application controllers extend this class.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Type
from flask import jsonify, render_template, redirect, url_for, request, session, abort


class Controller:
    """
    Base controller for Laraflask applications.
    Provides helpers for views, JSON, redirects, and validation.
    """

    # ─── View Responses ───────────────────────────────────────────────────────

    def view(self, template: str, data: Dict = None) -> str:
        """Render a BladePy / Jinja2 template."""
        return render_template(
            template.replace('.', '/') + '.blade.html',
            **(data or {})
        )

    def json(self, data: Any = None, status: int = 200) -> Any:
        """Return a JSON response."""
        return jsonify(data), status

    def respond(self, data: Any = None, message: str = 'OK', status: int = 200) -> Any:
        """Standardised API success response."""
        payload = {'success': True, 'message': message}
        if data is not None:
            payload['data'] = data
        return jsonify(payload), status

    def error(self, message: str = 'Error', status: int = 400,
              errors: Dict = None) -> Any:
        """Standardised API error response."""
        payload = {'success': False, 'message': message}
        if errors:
            payload['errors'] = errors
        return jsonify(payload), status

    def no_content(self):
        from flask import Response
        return Response(status=204)

    # ─── Redirect Responses ───────────────────────────────────────────────────

    def back(self, fallback: str = '/') -> Any:
        """Redirect back to the previous URL."""
        back_url = request.referrer or url_for(fallback)
        return redirect(back_url)

    def redirect_to(self, url: str, status: int = 302) -> Any:
        return redirect(url, status)

    def redirect_route(self, name: str, status: int = 302, **kwargs) -> Any:
        return redirect(url_for(name, **kwargs), status)

    def redirect_with_success(self, url: str, message: str) -> Any:
        session['success'] = message
        return redirect(url)

    def redirect_with_error(self, url: str, message: str) -> Any:
        session['error'] = message
        return redirect(url)

    def redirect_back_with_errors(self, errors: Dict, input: Dict = None) -> Any:
        session['errors'] = errors
        if input:
            session['_old_input'] = input
        return self.back()

    # ─── Validation ───────────────────────────────────────────────────────────

    def validate(self, data: Dict, rules: Dict,
                 messages: Dict = None) -> Dict:
        """Validate data and return validated fields, or abort 422."""
        from laraflask.validation.validator import Validator, ValidationException
        try:
            return Validator(data, rules, messages).validate()
        except ValidationException as e:
            if request.is_json or request.path.startswith('/api/'):
                abort(422, description=str(e))
            self.redirect_back_with_errors(e.errors, data)
            abort(422)

    def validate_request(self, rules: Dict, messages: Dict = None) -> Dict:
        """Validate the current request."""
        data = {
            **request.form.to_dict(),
            **request.args.to_dict(),
            **(request.get_json(silent=True) or {}),
        }
        return self.validate(data, rules, messages)

    # ─── Input Helpers ────────────────────────────────────────────────────────

    def input(self, key: str, default: Any = None) -> Any:
        """Get a request input value."""
        return (request.form.get(key)
                or request.args.get(key)
                or (request.get_json(silent=True) or {}).get(key)
                or default)

    def all_input(self) -> Dict:
        """Get all request input."""
        data = {}
        data.update(request.args.to_dict())
        data.update(request.form.to_dict())
        if request.is_json:
            data.update(request.get_json(silent=True) or {})
        return data

    def only(self, *keys: str) -> Dict:
        """Get only the specified input keys."""
        all_data = self.all_input()
        return {k: all_data.get(k) for k in keys}

    def except_(self, *keys: str) -> Dict:
        """Get all input except the specified keys."""
        all_data = self.all_input()
        return {k: v for k, v in all_data.items() if k not in keys}

    # ─── Auth Helpers ─────────────────────────────────────────────────────────

    def auth_user(self) -> Optional[Any]:
        """Get the authenticated user."""
        from laraflask.auth.auth import Auth
        return Auth.user()

    def is_authenticated(self) -> bool:
        from laraflask.auth.auth import Auth
        return Auth.check()

    def authorize(self, ability: str, model: Any = None) -> None:
        """Abort 403 if gate check fails."""
        from laraflask.auth.auth import Gate
        Gate.authorize(ability, model)

    # ─── Pagination ───────────────────────────────────────────────────────────

    def paginate(self, query_builder, per_page: int = 15,
                 resource_class=None) -> Any:
        page = request.args.get('page', 1, type=int)
        paginator = query_builder.paginate(per_page=per_page, page=page)

        if resource_class:
            from laraflask.api.api import ApiResourceCollection
            return (ApiResourceCollection(paginator['data'], resource_class)
                    .paginate(paginator)
                    .to_response())

        return jsonify({
            'success': True,
            'data': [
                item.to_dict() if hasattr(item, 'to_dict') else item
                for item in paginator['data']
            ],
            'meta': {
                'total':        paginator['total'],
                'per_page':     paginator['per_page'],
                'current_page': paginator['current_page'],
                'last_page':    paginator['last_page'],
            },
        })
