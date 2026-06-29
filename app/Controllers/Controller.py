"""
Laraflask Base Controller
All application controllers extend this class.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Response as FlaskResponse

# Type alias for controller return values (Flask response types)
ControllerResponse = Any


class Controller:
    """
    Base controller for Laraflask applications.

    Provides helpers for views, JSON responses, redirects, validation,
    input access, authentication, and pagination.

    Subclasses may override ``middleware()`` to declare route-level middleware
    or use ``__init_subclass__`` for automatic registration.
    """

    # ─── Middleware Declaration ────────────────────────────────────────────────
    # Override in subclasses to declare middleware that should run before
    # actions in this controller:
    #
    #   class PostController(Controller):
    #       @classmethod
    #       def middleware(cls) -> List[str]:
    #           return ['auth', 'verified']
    #
    # The framework's router can inspect this list when registering routes.

    @classmethod
    def middleware(cls) -> List[str]:
        """
        Return a list of middleware names that apply to this controller.

        Override in subclasses to restrict access or run pre/post processing.
        By default no middleware is declared.
        """
        return []

    # Hook for subclass registration. Override in advanced scenarios to
    # perform setup when a controller subclass is defined:
    #
    #   def __init_subclass__(cls, **kwargs):
    #       super().__init_subclass__(**kwargs)
    #       # e.g., auto-register middleware from cls.middleware()

    # ─── View Responses ───────────────────────────────────────────────────────

    def view(self, template: str, data: Optional[Dict[str, Any]] = None) -> str:
        """
        Render a BladePy / Jinja2 template.

        Args:
            template: Dot-notation template path (e.g. 'posts.index').
            data: Context variables passed to the template.

        Returns:
            Rendered HTML string.
        """
        from flask import render_template
        return render_template(
            template.replace('.', '/') + '.blade.html',
            **(data or {})
        )

    def json(self, data: Any = None, status: int = 200) -> ControllerResponse:
        """
        Return a JSON response.

        Args:
            data: Serialisable payload.
            status: HTTP status code.

        Returns:
            Tuple of (Response, status).
        """
        from flask import jsonify
        return jsonify(data), status

    def respond(self, data: Any = None, message: str = 'OK',
                status: int = 200) -> ControllerResponse:
        """
        Standardised API success response.

        Args:
            data: Response payload.
            message: Human-readable message.
            status: HTTP status code.

        Returns:
            Tuple of (ApiResponse, status).
        """
        from laraflask.api.api import ApiResponse
        return ApiResponse.success(data=data, message=message), status

    def error(self, message: str = 'Error', status: int = 400,
              errors: Optional[Dict[str, Any]] = None) -> ControllerResponse:
        """
        Standardised API error response.

        Args:
            message: Error description.
            status: HTTP status code.
            errors: Field-level error details.

        Returns:
            Tuple of (ApiResponse, status).
        """
        from laraflask.api.api import ApiResponse
        return ApiResponse.error(message=message, errors=errors or {}), status

    def no_content(self) -> ControllerResponse:
        """
        Return a 204 No Content response.

        Returns:
            Empty response with status 204.
        """
        from flask import Response
        return Response(status=204)

    # ─── Redirect Responses ───────────────────────────────────────────────────

    def back(self, fallback: str = '/') -> ControllerResponse:
        """
        Redirect back to the previous URL.

        Args:
            fallback: URL to use when no referrer is available.

        Returns:
            Redirect response.
        """
        from flask import redirect, url_for, request
        back_url = request.referrer or url_for(fallback)
        return redirect(back_url)

    def redirect_to(self, url: str, status: int = 302) -> ControllerResponse:
        """
        Redirect to an absolute URL.

        Args:
            url: Target URL.
            status: HTTP redirect status (302 or 301).

        Returns:
            Redirect response.
        """
        from flask import redirect
        return redirect(url, status)

    def redirect_route(self, name: str, status: int = 302,
                       **kwargs: Any) -> ControllerResponse:
        """
        Redirect to a named route.

        Args:
            name: Route endpoint name.
            status: HTTP redirect status.
            **kwargs: URL parameters for the route.

        Returns:
            Redirect response.
        """
        from flask import redirect, url_for
        return redirect(url_for(name, **kwargs), status)

    def redirect_with_success(self, url: str,
                              message: str) -> ControllerResponse:
        """
        Redirect with a success flash message.

        Args:
            url: Target URL.
            message: Success message stored in session.

        Returns:
            Redirect response.
        """
        from flask import redirect, session
        session['success'] = message
        return redirect(url)

    def redirect_with_error(self, url: str,
                            message: str) -> ControllerResponse:
        """
        Redirect with an error flash message.

        Args:
            url: Target URL.
            message: Error message stored in session.

        Returns:
            Redirect response.
        """
        from flask import redirect, session
        session['error'] = message
        return redirect(url)

    def redirect_back_with_errors(self, errors: Dict[str, Any],
                                  input: Optional[Dict[str, Any]] = None) -> ControllerResponse:
        """
        Redirect back with validation errors and old input.

        Args:
            errors: Field-level validation errors.
            input: Old input to flash for re-population.

        Returns:
            Redirect response.
        """
        from flask import session
        session['errors'] = errors
        if input:
            session['_old_input'] = input
        return self.back()

    # ─── Validation ───────────────────────────────────────────────────────────

    def validate(self, data: Dict[str, Any], rules: Dict[str, Any],
                 messages: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Validate data against rules. Aborts 422 on failure.

        Args:
            data: Input data to validate.
            rules: Validation rules keyed by field name.
            messages: Custom error messages.

        Returns:
            Dict of validated fields.

        Raises:
            422 abort on validation failure.
        """
        from flask import request, abort
        from laraflask.validation.validator import Validator, ValidationException
        try:
            return Validator(data, rules, messages).validate()
        except ValidationException as e:
            if request.is_json or request.path.startswith('/api/'):
                abort(422, description=str(e))
            self.redirect_back_with_errors(e.errors, data)
            abort(422)

    def validate_request(self, rules: Dict[str, Any],
                         messages: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Validate the current request's combined input.

        Merges form data, query parameters, and JSON body before validating.

        Args:
            rules: Validation rules keyed by field name.
            messages: Custom error messages.

        Returns:
            Dict of validated fields.
        """
        from flask import request
        data: Dict[str, Any] = {
            **request.form.to_dict(),
            **request.args.to_dict(),
            **(request.get_json(silent=True) or {}),
        }
        return self.validate(data, rules, messages)

    # ─── Input Helpers ────────────────────────────────────────────────────────

    def input(self, key: str, default: Any = None) -> Any:
        """
        Get a single request input value.

        Checks form data, query string, and JSON body in order.

        Args:
            key: Input field name.
            default: Value to return if key is not present.

        Returns:
            The input value or default.
        """
        from flask import request
        return (request.form.get(key)
                or request.args.get(key)
                or (request.get_json(silent=True) or {}).get(key)
                or default)

    def all_input(self) -> Dict[str, Any]:
        """
        Get all request input merged from all sources.

        Returns:
            Dict of all input fields.
        """
        from flask import request
        data: Dict[str, Any] = {}
        data.update(request.args.to_dict())
        data.update(request.form.to_dict())
        if request.is_json:
            data.update(request.get_json(silent=True) or {})
        return data

    def only(self, *keys: str) -> Dict[str, Any]:
        """
        Get only the specified input keys.

        Args:
            *keys: Field names to include.

        Returns:
            Dict containing only the requested keys.
        """
        all_data = self.all_input()
        return {k: all_data.get(k) for k in keys}

    def except_(self, *keys: str) -> Dict[str, Any]:
        """
        Get all input except the specified keys.

        Args:
            *keys: Field names to exclude.

        Returns:
            Dict of input with specified keys removed.
        """
        all_data = self.all_input()
        return {k: v for k, v in all_data.items() if k not in keys}

    # ─── Auth Helpers ─────────────────────────────────────────────────────────

    def auth_user(self) -> Optional[Any]:
        """
        Get the currently authenticated user.

        Returns:
            The authenticated user model instance, or None.
        """
        from laraflask.auth.auth import Auth
        return Auth.user()

    def is_authenticated(self) -> bool:
        """
        Check whether a user is authenticated.

        Returns:
            True if a user is logged in.
        """
        from laraflask.auth.auth import Auth
        return Auth.check()

    def authorize(self, ability: str, model: Any = None) -> None:
        """
        Abort 403 if the current user lacks the given ability.

        Args:
            ability: Gate ability name.
            model: Optional model instance to check against.

        Raises:
            403 abort if authorization fails.
        """
        from laraflask.auth.auth import Gate
        Gate.authorize(ability, model)

    # ─── Pagination ───────────────────────────────────────────────────────────

    def paginate(self, query_builder: Any, per_page: int = 15,
                 resource_class: Optional[Type[Any]] = None) -> ControllerResponse:
        """
        Paginate a query builder result.

        Args:
            query_builder: ORM query builder instance.
            per_page: Items per page.
            resource_class: Optional API resource class for transformation.

        Returns:
            JSON response with paginated data and meta information.
        """
        from flask import request, jsonify
        page: int = request.args.get('page', 1, type=int)
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
