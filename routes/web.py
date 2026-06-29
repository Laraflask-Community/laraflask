"""
Web Routes - Laraflask
======================

Define stateful, session-based web routes here. These routes are intended
for browser clients and support sessions, CSRF protection, and cookies.

`Route` is injected automatically by the framework at runtime.
Do NOT import it -- use it directly as a module-level global.
"""

from laraflask.api.api import ApiResponse


# =============================================================================
# Configuration
# =============================================================================

APP_NAME = 'Laraflask'
APP_VERSION = '1.3.0'
APP_TAGLINE = 'Elegant . Expressive . Modern . Fast . Scalable'


# =============================================================================
# Welcome / Public Routes
# =============================================================================

Route.get('/', lambda: ApiResponse.success(data={
    'framework': APP_NAME,
    'version':   APP_VERSION,
    'tagline':   APP_TAGLINE,
    'status':    'running',
})).name('welcome')


# =============================================================================
# Authentication Routes
# =============================================================================
# Uncomment to enable session-based authentication for web clients.

# Route.get('/login',   'App\\Controllers\\Auth\\LoginController@show_form').name('login')
# Route.post('/login',  'App\\Controllers\\Auth\\LoginController@login')
# Route.post('/logout', 'App\\Controllers\\Auth\\LoginController@logout').name('logout')

# Route.get('/register',  'App\\Controllers\\Auth\\RegisterController@show_form').name('register')
# Route.post('/register', 'App\\Controllers\\Auth\\RegisterController@register')


# =============================================================================
# Dashboard (Authenticated)
# =============================================================================
# Routes within this group require the 'auth' middleware -- unauthenticated
# users will be redirected to the login page.

# with Route.group({'prefix': '/dashboard', 'middleware': ['auth']}):
#     Route.get('/',        'App\\Controllers\\DashboardController@index').name('dashboard')
#     Route.get('/profile', 'App\\Controllers\\DashboardController@profile').name('dashboard.profile')


# =============================================================================
# Resource Routes
# =============================================================================
# Full CRUD resource routing. Use `only` or `except_` to limit actions.

# Route.resource('posts',    'App\\Controllers\\PostController')
# Route.resource('users',    'App\\Controllers\\UserController', only=['index', 'show'])
# Route.resource('comments', 'App\\Controllers\\CommentController', except_=['create', 'edit'])
