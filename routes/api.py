"""
API Routes - Laraflask
======================

Define stateless API routes here. All endpoints return JSON via ApiResponse.
Authentication should use JWT tokens or API keys (not sessions).

`Route` is injected automatically by the framework at runtime.
Do NOT import it -- use it directly as a module-level global.
"""

from laraflask.api.api import ApiResponse


# =============================================================================
# Configuration
# =============================================================================

API_VERSION = 'v1'
API_PREFIX = f'/api/{API_VERSION}'
FRAMEWORK_VERSION = '1.3.0'


# =============================================================================
# Route Definitions - API v1
# =============================================================================

def register_health_routes():
    """Health check and status endpoints."""
    Route.get('/health', lambda: ApiResponse.success(data={
        'status':    'ok',
        'version':   API_VERSION,
        'framework': f'Laraflask {FRAMEWORK_VERSION}',
    }))


def register_auth_routes():
    """Authentication endpoints (login, register, token refresh, logout)."""
    # Route.post('/auth/login',    'App\\Controllers\\Api\\V1\\AuthController@login')
    # Route.post('/auth/register', 'App\\Controllers\\Api\\V1\\AuthController@register')
    #
    # with Route.group({'middleware': ['auth:api']}):
    #     Route.post('/auth/refresh', 'App\\Controllers\\Api\\V1\\AuthController@refresh')
    #     Route.post('/auth/logout',  'App\\Controllers\\Api\\V1\\AuthController@logout')
    pass


def register_resource_routes():
    """RESTful resource endpoints for domain entities."""
    # Route.api_resource('users',    'App\\Controllers\\Api\\V1\\UserController')
    # Route.api_resource('posts',    'App\\Controllers\\Api\\V1\\PostController')
    # Route.api_resource('products', 'App\\Controllers\\Api\\V1\\ProductController')
    # Route.api_resource('comments', 'App\\Controllers\\Api\\V1\\CommentController')
    pass


# =============================================================================
# Route Registration
# =============================================================================
# All API v1 routes are registered under the /api/v1 prefix.
# Add middleware (e.g., 'throttle:60,1') to the list below when needed.

with Route.group({'prefix': API_PREFIX, 'middleware': []}):
    register_health_routes()
    register_auth_routes()
    register_resource_routes()
