"""
API Routes — Laraflask
Define stateless API routes here. JWT / API Key auth recommended.

`Route` is injected automatically by the framework — do NOT import Flask
or laraflask.routing.router here. Use `ApiResponse` for all JSON responses.
"""

from laraflask.api.api import ApiResponse

# ─── API v1 ───────────────────────────────────────────────────────────────────

def register_v1():
    Route.get('/health', lambda: ApiResponse.success(data={
        'status':    'ok',
        'version':   'v1',
        'framework': 'Laraflask 1.3.0',
    }))

    # Route.api_resource('users',    'App\\Controllers\\Api\\V1\\UserController')
    # Route.api_resource('posts',    'App\\Controllers\\Api\\V1\\PostController')
    # Route.api_resource('products', 'App\\Controllers\\Api\\V1\\ProductController')

    # Auth endpoints
    # Route.post('/auth/login',    'App\\Controllers\\Api\\V1\\AuthController@login')
    # Route.post('/auth/register', 'App\\Controllers\\Api\\V1\\AuthController@register')
    # Route.post('/auth/refresh',  'App\\Controllers\\Api\\V1\\AuthController@refresh').middleware('auth:api')
    # Route.post('/auth/logout',   'App\\Controllers\\Api\\V1\\AuthController@logout').middleware('auth:api')


# Register under /api/v1 prefix
with Route.group({'prefix': '/api/v1', 'middleware': []}):
    register_v1()
