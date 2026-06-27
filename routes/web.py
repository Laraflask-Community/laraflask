"""
Web Routes — Laraflask
Define stateful, session-based web routes here.
"""

from flask import render_template, redirect, url_for, session, jsonify

# Route is injected automatically by the framework
# from laraflask.routing.router import Router as Route

# ─── Welcome ──────────────────────────────────────────────────────────────────

Route.get('/', lambda: jsonify({
    'framework': 'Laraflask',
    'version': '1.0.0',
    'tagline': 'Elegant · Expressive · Modern · Fast · Scalable',
    'status': 'running',
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
