"""
Web Routes — Laraflask
Define stateful, session-based web routes here.

`Route` is injected automatically by the framework — do NOT import Flask
or laraflask.routing.router here. Use `Route` directly for all routing,
and `ApiResponse` (or `self.respond()` inside controllers) for responses.
"""

# ─── Welcome ──────────────────────────────────────────────────────────────────

Route.view('/', 'welcome', {
    'features': [
        {'icon': '🚀', 'title': 'Eloquent-style ORM', 'desc': 'Active Record models on top of SQLAlchemy.', 'color': '#6366f1'},
        {'icon': '🛠️', 'title': 'Artisan CLI', 'desc': 'Generators, migrations, queue workers, and Tinker.', 'color': '#22c55e'},
        {'icon': '🧩', 'title': 'Service Container', 'desc': 'Dependency injection with contextual binding & tagging.', 'color': '#f59e0b'},
        {'icon': '🧱', 'title': 'BladePy Templates', 'desc': 'Blade-like directives compiled down to Jinja2.', 'color': '#ec4899'},
        {'icon': '📨', 'title': 'Queue & Jobs', 'desc': 'Background jobs with graceful, interruptible workers.', 'color': '#0ea5e9'},
        {'icon': '🧪', 'title': 'Testing Toolkit', 'desc': 'Unit/feature tests with fakes for events, mail, and queues.', 'color': '#8b5cf6'},
    ],
    'stats': [
        {'value': '20+', 'label': 'Modules'},
        {'value': '100%', 'label': 'Python'},
        {'value': 'MIT', 'label': 'Licensed'},
        {'value': 'v1.4.0', 'label': 'Latest'},
    ],
})


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
