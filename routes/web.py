"""
Web Routes — Laraflask
Define stateful, session-based web routes here.

`Route` is injected automatically by the framework — do NOT import Flask
or laraflask.routing.router here. Use `Route` directly for all routing,
and `ApiResponse` (or `self.respond()` inside controllers) for responses.
"""

from laraflask.api.api import ApiResponse

# ─── Welcome ──────────────────────────────────────────────────────────────────

Route.get('/', lambda: ApiResponse.success(data={
    'framework': 'Laraflask',
    'version':   '1.3.0',
    'tagline':   'Elegant · Expressive · Modern · Fast · Scalable',
    'status':    'running',
})).name('welcome')


# ─── Auth ─────────────────────────────────────────────────────────────────────

# Route.get('/login',  'App\\Controllers\\Auth\\LoginController@show_form').name('login')
# Route.post('/login', 'App\\Controllers\\Auth\\LoginController@login')
# Route.post('/logout','App\\Controllers\\Auth\\LoginController@logout').name('logout')

# Route.get('/register',  'App\\Controllers\\Auth\\RegisterController@show_form').name('register')
# Route.post('/register', 'App\\Controllers\\Auth\\RegisterController@register')


# ─── Dashboard ────────────────────────────────────────────────────────────────

# with Route.group({'prefix': '/dashboard', 'middleware': ['auth']}):
#     Route.get('/', 'App\\Controllers\\DashboardController@index').name('dashboard')


# ─── Resource Routes ──────────────────────────────────────────────────────────

# Route.resource('posts',    'App\\Controllers\\PostController')
# Route.resource('users',    'App\\Controllers\\UserController', only=['index', 'show'])
# Route.resource('comments', 'App\\Controllers\\CommentController', except_=['create', 'edit'])
