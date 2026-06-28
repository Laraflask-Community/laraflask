# Laraflask v1.4.0

**A Laravel-inspired framework for Python — built on top of Flask + SQLAlchemy.**
Elegant. Expressive. Modern.

Laraflask brings Laravel's developer experience philosophy to the Python ecosystem: an Eloquent-style ORM, an Artisan CLI, a Service Container with dependency injection, Blade-like templating, a Job Queue, a Task Scheduler, and more than 20 other ready-to-use modules — all with an API that feels familiar to anyone who has ever written Laravel code.

```python
# Feels like Laravel, written in Python
class PostController(Controller):
    def index(self):
        posts = Post.where('published', True).order_by_desc('created_at').paginate(15)
        return PostResource.collection(posts)

    def store(self):
        data = StorePostRequest().validate()
        post = Post.create(data)
        Events.dispatch(PostCreated(post))
        return PostResource(post).to_response()
```

---

## Table of Contents

- [Installation](#installation)
- [Creating a New Project](#creating-a-new-project)
- [Directory Structure](#directory-structure)
- [Core Concepts](#core-concepts)
  - [Application & Service Container](#application--service-container)
  - [Service Provider](#service-provider)
  - [Configuration](#configuration)
- [Routing](#routing)
- [Controllers](#controllers)
- [ORM (EloquentPy)](#orm-eloquentpy)
  - [Model](#model)
  - [Query Builder](#query-builder)
  - [Collection](#collection)
  - [Relationships](#relationships)
  - [Model Observers](#model-observers)
  - [Migrations & Schema](#migrations--schema)
  - [Vector Similarity Search (pgvector)](#vector-similarity-search-pgvector)
- [Validation (Validator & FormRequest)](#validation-validator--formrequest)
- [Authentication (Auth)](#authentication-auth)
- [Authorization (Gate & Policy)](#authorization-gate--policy)
- [Middleware](#middleware)
- [Security (CSRF, XSS, Encryption)](#security-csrf-xss-encryption)
- [Cache](#cache)
- [Events & Listeners](#events--listeners)
- [Queue & Jobs](#queue--jobs)
- [Task Scheduler](#task-scheduler)
- [Notifications](#notifications)
- [Storage / Filesystem](#storage--filesystem)
- [Template Engine (BladePy)](#template-engine-bladepy)
- [API Resource & JSON:API](#api-resource--jsonapi)
- [WebSocket & Broadcasting](#websocket--broadcasting)
- [Testing](#testing)
- [Artisan CLI](#artisan-cli)
- [Tinker (Interactive REPL)](#tinker-interactive-repl)
- [Advanced Container (Contextual Binding & Tagging)](#advanced-container-contextual-binding--tagging)
- [Macroable](#macroable)
- [Exception Handling](#exception-handling)
- [Deployment](#deployment)
- [Changelog](#changelog)
- [Known Limitations](#known-limitations)
- [License](#license)
- [Contributing](#contributing)

---

## Installation

### Requirements

- Python ≥ 3.10
- pip
- (Optional) MySQL / PostgreSQL / Redis for production

### Clone the Repository

```bash
git clone https://github.com/Laraflask-Community/laraflask.git
cd laraflask
```

### Install via pip

```bash
# Minimal — Flask + SQLAlchemy only
pip install laraflask-core

# With all optional features
pip install laraflask-core[all]
```

### Install Per-Feature (Extras)

Laraflask uses *extras* to keep dependencies lightweight — install only what you need:

| Extra | Command | Purpose |
|---|---|---|
| `mysql` | `pip install laraflask-core[mysql]` | MySQL driver (PyMySQL) |
| `postgresql` | `pip install laraflask-core[postgresql]` | PostgreSQL driver (psycopg2) |
| `vector` | `pip install laraflask-core[vector]` | pgvector for semantic/similarity search |
| `redis` | `pip install laraflask-core[redis]` | Redis for cache & queue |
| `auth` | `pip install laraflask-core[auth]` | bcrypt + PyJWT + cryptography |
| `queue` | `pip install laraflask-core[queue]` | Celery + Kombu |
| `storage` | `pip install laraflask-core[storage]` | Amazon S3 (boto3) |
| `notifications` | `pip install laraflask-core[notifications]` | Twilio (SMS/WhatsApp) |
| `websocket` | `pip install laraflask-core[websocket]` | Flask-SocketIO |
| `testing` | `pip install laraflask-core[testing]` | pytest + factory-boy + faker |
| `dev` | `pip install laraflask-core[dev]` | Full development toolchain |
| `production` | `pip install laraflask-core[production]` | Gunicorn + Gevent |

> 💡 Some features (bcrypt, PyJWT, cryptography) use *graceful degradation* — if not installed, Laraflask automatically falls back to a simpler implementation (fine for development, **not recommended for production**).

---

## Creating a New Project

```bash
# Copy the environment file
cp .env.example .env

# Generate APP_KEY
python artisan.py key:generate

# Run migrations
python artisan.py migrate

# (Optional) seed initial data
python artisan.py db:seed

# Start the development server
python laraflask.py
# or
python artisan.py serve
```

The application will run at `http://127.0.0.1:8000`.

### Environment Configuration (.env)

```bash
APP_NAME=Laraflask
APP_ENV=local
APP_KEY=base64:result_of_key_generate
APP_DEBUG=true
APP_URL=http://localhost:8000
APP_TIMEZONE=UTC
APP_LOCALE=en

# Database
DB_CONNECTION=sqlite
DB_DATABASE=database/laraflask.db

# Cache
CACHE_DRIVER=file

# Session
SESSION_DRIVER=filesystem

# Queue
QUEUE_CONNECTION=sync
```

See `.env.example` for the full list of variables (Redis, Mail, AWS S3, JWT, Telegram, Twilio, Firebase).

## Directory Structure

### Framework Package (`laraflask-core`)

```
laraflask/
├── core/            — Application, Container, Config, Exceptions, Providers,
│                      Collection, Macroable, Model decorators (@table, etc.)
├── routing/         — Router, Route, RouteGroup
├── orm/             — Model (EloquentPy), DB, QueryBuilder, Migration, Schema
├── auth/            — Auth, JWT, Hash, Gate, Policy, Guards
├── cache/           — Cache (File, Redis, Database, Array drivers)
├── events/          — EventDispatcher, Event, Listener, Subscriber
├── queue/           — Queue, Job, Interruptible, Worker
├── scheduler/       — Schedule, ScheduledEvent
├── security/        — CsrfToken, PreventRequestForgery, XSS, Crypt
├── storage/         — Storage (Local, S3 drivers)
├── notifications/   — Notification, Mail, SMS, Telegram, WhatsApp, Push
├── middleware/      — Middleware base + built-in middleware
├── api/              — ApiResponse, ApiResource, JsonApiResource, RateLimiter
├── validation/      — Validator, FormRequest
├── template/        — BladePy template engine
├── testing/         — TestCase, FeatureTestCase, Fakes
├── ws/              — WebSocket & SSE (Server-Sent Events)
└── console/         — Artisan CLI commands
```

### Application Project Structure (result of `laraflask new`)

```
my-app/
├── app/
│   ├── Console/            — Custom Artisan commands
│   ├── Controllers/        — Controllers
│   ├── Events/             — Application events
│   ├── Exceptions/
│   │   └── Handler.py      — Global exception handler
│   ├── Jobs/                — Queue jobs
│   ├── Listeners/          — Event listeners
│   ├── Middleware/         — Application middleware
│   ├── Models/             — Eloquent-style models
│   ├── Notifications/      — Notification classes
│   ├── Policies/           — Authorization policies
│   ├── Providers/          — Application service providers
│   ├── Requests/           — FormRequests
│   ├── Services/           — Service / business-logic classes
│   └── Traits/             — Reusable mixins/traits
├── config/                  — Configuration files (app, database, cache, etc.)
├── database/
│   ├── factories/          — Model factories (for testing/seeding)
│   ├── migrations/         — Migrations
│   └── seeders/            — Database seeders
├── resources/
│   └── views/              — BladePy templates (.blade.html)
├── routes/
│   ├── web.py               — Web routes (session-based)
│   ├── api.py               — API routes (stateless)
│   └── console.py           — Custom Artisan command routes
├── storage/
│   ├── app/                 — Application-uploaded files
│   ├── framework/           — Cache, session, compiled views
│   └── logs/
├── public/                  — Public assets (web server entry point)
├── tests/
│   ├── Unit/                 — Unit tests
│   └── Feature/              — Feature/integration tests
├── .env                      — Active environment (never commit this)
├── .env.example
├── artisan.py                — Artisan CLI entry point
├── laraflask.py               — Server entry point (`python laraflask.py`)
└── conftest.py
```

---

## Core Concepts

### Application & Service Container

`Application` is the heart of the framework — it **extends `Container`** (the IoC container), so every dependency-injection feature of the container is automatically available at the application level.

```python
from laraflask.core.application import Application

app = Application(base_path='/path/to/my-app')
app.bootstrap()        # boots every service provider
flask_app = app.get_flask()   # grab the underlying Flask instance
```

**Path Helpers** (following Laravel's `app_path()`, `base_path()`, etc. pattern):

```python
app.path('public')          # base_path/public
app.app_path('Models')      # base_path/app/Models
app.config_path()           # base_path/config
app.database_path()         # base_path/database
app.resource_path('views')  # base_path/resources/views
app.storage_path()          # base_path/storage
app.public_path()           # base_path/public
app.routes_path()           # base_path/routes
```

**Environment checks:**

```python
app.environment()                 # 'local' | 'production' | 'testing'
app.environment('local', 'staging')  # True if the environment matches either one
app.is_production()
app.is_local()
app.is_testing()
```

#### Service Container — Binding & Resolving

The Laraflask container supports **regular binding**, **singletons**, **instances**, **contextual binding**, and **tagging**.

```python
from laraflask.core.container import Container

container = Container()

# Regular binding — a new instance every resolve
container.bind(PaymentGateway, StripeGateway)

# Singleton — the same instance every resolve
container.singleton(Logger, FileLogger)

# Instance — register an already-existing object
container.instance('config', config_object)

# Resolve
gateway = container.make(PaymentGateway)

# Automatic dependency injection based on type hints
class OrderService:
    def __init__(self, gateway: PaymentGateway):
        self.gateway = gateway

service = container.make(OrderService)  # gateway is automatically resolved
```

#### Contextual Binding

Provide a **different** implementation depending on which class is currently being built — extremely useful when two parts of your application need the same interface but different implementations.

```python
container.when(ReportController).needs(Logger).give(FileLogger)
container.when(UserController).needs(Logger).give(DatabaseLogger)

report_controller = container.make(ReportController)  # logger -> FileLogger
user_controller   = container.make(UserController)    # logger -> DatabaseLogger
```

#### Tagging

Register several bindings under a single "tag", then resolve all of them at once — great for patterns like a list of report generators, a list of payment providers, etc.

```python
container.tag([PdfReport, CsvReport, ExcelReport], 'reports')

for report in container.tagged('reports'):
    report.generate()
```

### Service Provider

A Service Provider is the central place for **registering** (`register()`) and **booting** (`boot()`) services into the container. All of Laraflask's core features (DB, Cache, Auth, Queue, etc.) are booted through built-in providers; you add your own providers for application logic.

```bash
python artisan.py make:provider AppServiceProvider
```

```python
# app/Providers/AppServiceProvider.py
from laraflask.core.providers import ServiceProvider

class AppServiceProvider(ServiceProvider):
    def register(self):
        # Register container bindings here
        self.app.singleton('payment', lambda app: StripeGateway())

    def boot(self):
        # Logic that requires every other provider to already be registered
        pass
```

Register your provider in `config/app.py`:

```python
config = {
    'providers': [
        'app.Providers.AppServiceProvider.AppServiceProvider',
        'app.Providers.AuthServiceProvider.AuthServiceProvider',
        'app.Providers.EventServiceProvider.EventServiceProvider',
    ],
}
```

**Built-in framework providers** (automatically booted on `app.bootstrap()`):

| Provider | Responsibility |
|---|---|
| `RouteServiceProvider` | Loads route files |
| `DatabaseServiceProvider` | Database connection |
| `CacheServiceProvider` | Cache driver configuration |
| `SessionServiceProvider` | Flask session configuration |
| `AuthServiceProvider` | Authentication guards + Gate |
| `ValidationServiceProvider` | `Validator` binding |
| `EventServiceProvider` | Listener registration |
| `QueueServiceProvider` | Queue connection configuration |
| `NotificationServiceProvider` | `NotificationSender` binding |
| `StorageServiceProvider` | Storage disk configuration |
| `SchedulerServiceProvider` | `Schedule` binding |

### Configuration

Every file in `config/*.py` is automatically loaded and accessed via dot-notation:

```python
from laraflask.core.config import Config

config = Config('/path/to/config')

config.get('database.connections.mysql.host')
config.get('app.providers')
config.get('cache.default', 'file')   # with a default value

config.set('app.debug', True)         # set at runtime
config.has('mail.mailers.smtp')
```

Every config file simply exports a dict named `config`:

```python
# config/app.py
import os

config = {
    'name': os.getenv('APP_NAME', 'Laraflask'),
    'env': os.getenv('APP_ENV', 'production'),
    'debug': os.getenv('APP_DEBUG', 'false').lower() == 'true',
    'providers': [...],
    'aliases': {
        'Auth': 'laraflask.auth.auth.Auth',
        'DB': 'laraflask.orm.db.DB',
        # ...
    },
}
```

## Routing

Routes are defined in `routes/web.py` (session-based) and `routes/api.py` (stateless). The `Route` object is automatically injected by the framework — no manual import needed.

### Basic Routes

```python
Route.get('/', lambda: 'Hello Laraflask')
Route.post('/posts', 'App\\Controllers\\PostController@store')
Route.put('/posts/{id}', 'App\\Controllers\\PostController@update')
Route.patch('/posts/{id}', 'App\\Controllers\\PostController@update')
Route.delete('/posts/{id}', 'App\\Controllers\\PostController@destroy')
Route.any('/webhook', 'App\\Controllers\\WebhookController@handle')
Route.match(['GET', 'POST'], '/contact', 'App\\Controllers\\ContactController@handle')
```

### Route Parameters

```python
Route.get('/posts/{id}', 'App\\Controllers\\PostController@show')
Route.get('/posts/{id}/comments/{comment}', 'App\\Controllers\\CommentController@show')
```

### Named Routes & `url_for`

```python
Route.get('/dashboard', 'App\\Controllers\\DashboardController@index').name('dashboard')

# Elsewhere:
router.url_for('dashboard')
```

### Per-Route Middleware

```python
Route.get('/profile', 'App\\Controllers\\ProfileController@show').middleware('auth')
Route.post('/admin/users', 'App\\Controllers\\AdminController@store').middleware('auth', 'admin')
```

### Route Groups

```python
with Route.group({'prefix': '/dashboard', 'middleware': ['auth']}):
    Route.get('/', 'App\\Controllers\\DashboardController@index').name('dashboard')
    Route.get('/settings', 'App\\Controllers\\DashboardController@settings')

# Or as separate context managers
with Route.prefix('/api/v1'):
    Route.get('/users', 'App\\Controllers\\UserController@index')

with Route.middleware('auth', 'verified'):
    Route.get('/billing', 'App\\Controllers\\BillingController@index')
```

### Resource Routes

Generate all 7 standard CRUD routes (`index`, `create`, `store`, `show`, `edit`, `update`, `destroy`) in a single call:

```python
Route.resource('posts', 'App\\Controllers\\PostController')

# Restrict which methods are generated
Route.resource('users', 'App\\Controllers\\UserController', only=['index', 'show'])
Route.resource('comments', 'App\\Controllers\\CommentController', except_=['create', 'edit'])

# API resource — automatically excludes create/edit (HTML forms)
Route.api_resource('posts', 'App\\Controllers\\Api\\PostController')
```

| Method | URI | Action | Route Name |
|---|---|---|---|
| GET | `/posts` | `index` | `posts.index` |
| GET | `/posts/create` | `create` | `posts.create` |
| POST | `/posts` | `store` | `posts.store` |
| GET | `/posts/{id}` | `show` | `posts.show` |
| GET | `/posts/{id}/edit` | `edit` | `posts.edit` |
| PUT | `/posts/{id}` | `update` | `posts.update` |
| DELETE | `/posts/{id}` | `destroy` | `posts.destroy` |

### Middleware Groups & Aliases

```python
router.middleware_group('web', ['session', 'csrf'])
router.middleware_group('api', ['throttle:60,1'])

router.alias_middleware('auth', AuthMiddleware)
router.alias_middleware('admin', AdminMiddleware)
```

### Redirects & Direct Views

```python
Route.redirect('/old-path', '/new-path')
Route.permanent_redirect('/old-path', '/new-path')  # 301
Route.view('/about', 'pages.about', {'title': 'About Us'})
```

### Inspecting Routes (Artisan)

```bash
python artisan.py route:list
```

---

## Controllers

Controllers receive dependencies through the container — including `FormRequest` instances, which are automatically validated before the method runs.

```python
# app/Controllers/PostController.py
from app.Controllers.Controller import Controller
from app.Models.Post import Post
from app.Requests.StorePostRequest import StorePostRequest
from laraflask.api.api import ApiResponse


class PostController(Controller):
    def index(self):
        posts = Post.where('published', True).paginate(15)
        return ApiResponse.success(posts.to_dict())

    def show(self, id):
        post = Post.find_or_fail(id)
        return ApiResponse.success(post.to_dict())

    def store(self):
        data = StorePostRequest().validate()
        post = Post.create(data)
        return ApiResponse.success(post.to_dict(), status=201)

    def update(self, id):
        post = Post.find_or_fail(id)
        post.update(StorePostRequest().validated())
        return ApiResponse.success(post.to_dict())

    def destroy(self, id):
        Post.find_or_fail(id).delete()
        return ApiResponse.success(message='Post deleted')
```

An action can be a **string** (`"Namespace\\Controller@method"`), a **tuple** `(ControllerClass, 'method')`, or a **callable** directly (closure/function) — all three are resolved through the container, so dependencies like `FormRequest` are automatically injected.

## ORM (EloquentPy)

EloquentPy is Laraflask's Active-Record ORM, built on top of SQLAlchemy but with a Laravel Eloquent-style API.

### Model

```python
# app/Models/Post.py
from laraflask.orm.model import Model


class Post(Model):
    __table__ = 'posts'                       # optional — defaults to the pluralized class name (Post -> posts)
    __primary_key__ = 'id'                     # default: 'id'
    __fillable__ = ['title', 'body', 'user_id']
    __hidden__ = ['internal_notes']
    __timestamps__ = True                      # default: True (created_at, updated_at handled automatically)
    __soft_deletes__ = False                   # set True if the table has a deleted_at column
    __appends__ = ['excerpt']                  # extra accessors that also appear in to_dict()
    __casts__ = {
        'metadata': 'json',
        'published_at': 'datetime',
        'is_featured': 'boolean',
    }

    # Mutator — automatically called when the attribute is set
    def set_title_attribute(self, value: str) -> str:
        return value.strip().title()

    # Accessor — automatically called on to_dict() / attribute access
    def get_excerpt_attribute(self) -> str:
        body = self._attributes.get('body', '')
        return body[:100] + '...' if len(body) > 100 else body

    # Relationships
    @property
    def author(self):
        from app.Models.User import User
        return self.belongs_to(User, foreign_key='user_id')

    @property
    def comments(self):
        from app.Models.Comment import Comment
        return self.has_many(Comment)
```

#### Declarative Style: Decorators as an Alternative to Class Attributes

Instead of writing `__table__`/`__hidden__`/`__fillable__` manually, you can use **decorators** (adapting Laravel 13's PHP Attributes to Python idioms) — both styles can be freely mixed, and existing models keep working unchanged:

```python
from laraflask.orm.model import Model, table, hidden, fillable

@table(name='posts', primary_key='post_id')
@hidden('internal_notes')
@fillable('title', 'body', 'user_id')
class Post(Model):
    pass
```

#### Basic CRUD

```python
# Create
post = Post.create(title='Hello World', body='...', user_id=1)

# Read
post = Post.find(1)
post = Post.find_or_fail(1)          # raises ModelNotFoundException if missing
all_posts = Post.all()
all_posts = Post.all(as_collection=True)   # returned as a Collection (see Collection section)

# Update
post.title = 'Updated Title'
post.save()
# or directly through a query
Post.where('id', 1).update({'title': 'Updated Title'})

# Delete
post.delete()
# or
Post.where('published', False).delete()

# firstOrCreate / updateOrCreate
post = Post.first_or_create({'slug': 'hello-world'}, {'title': 'Hello World'})
post = Post.update_or_create({'slug': 'hello-world'}, {'title': 'Updated Title'})
```

#### Advanced Attributes

```python
post.fill({'title': 'New Title', 'body': 'New body'})   # mass-assignment via __fillable__
post.is_dirty()                # True if any attribute has changed since loading
post.is_dirty('title')         # check a specific attribute
post.get_dirty()               # dict of changed attributes
post.fresh()                   # re-fetch from the DB (new instance)
post.refresh()                 # re-fetch from the DB (same instance, in-place)
post.to_dict()
post.to_json()
```

#### Soft Deletes

```python
class Post(Model):
    __soft_deletes__ = True   # the table must have a deleted_at column

post.delete()                  # soft delete (sets deleted_at)
post.restore()                 # restore (deleted_at = None)

Post.all()                     # automatically excludes soft-deleted records
Post.with_trashed().get()      # include soft-deleted records
Post.only_trashed().get()      # only soft-deleted records
```

### Query Builder

```python
Post.where('published', True).get()
Post.where('views', '>', 100).get()
Post.where('title', 'LIKE', '%laravel%').get()

Post.where_in('category_id', [1, 2, 3]).get()
Post.where_not_in('status', ['draft', 'archived']).get()
Post.where_null('deleted_at').get()
Post.where_not_null('published_at').get()
Post.where_between('views', [100, 1000]).get()
Post.where_like('title', '%python%').get()

Post.query().where('a', 1).or_where('b', 2).get()

Post.order_by('created_at', 'DESC').get()
Post.order_by_desc('views').get()
Post.latest().get()             # order by created_at DESC
Post.oldest().get()             # order by created_at ASC

Post.limit(10).get()
Post.query().offset(20).limit(10).get()

Post.query().select('id', 'title').distinct().get()

Post.query().join('users', 'posts.user_id', '=', 'users.id').get()
Post.query().left_join('comments', 'posts.id', '=', 'comments.post_id').get()

Post.query().with_relations('author', 'comments').get()   # eager loading
```

#### Aggregation & Inspection

```python
Post.count()
Post.where('published', True).count()
Post.query().sum('views')
Post.query().avg('rating')
Post.query().max('views')
Post.query().min('views')
Post.query().exists()
Post.query().doesnt_exist()
```

#### Pagination

```python
result = Post.where('published', True).paginate(per_page=15, page=2)
# result = {
#     'data': [...],
#     'total': 142,
#     'per_page': 15,
#     'current_page': 2,
#     'last_page': 10,
#     'from': 16,
#     'to': 30,
# }
```

#### Chunking & Memory-Safe Iteration

```python
def process(posts):
    for post in posts:
        post.send_to_search_index()

Post.query().chunk(100, process)         # process 100 rows per batch
Post.query().each(lambda post: post.reindex())   # iterate one at a time
```

#### `pluck()` & `to_list()`

```python
Post.query().pluck('title')                       # ['Title 1', 'Title 2', ...]
Post.query().pluck('title', key='id')              # {1: 'Title 1', 2: 'Title 2'}
Post.query().to_list()                              # [{'id': 1, 'title': '...'}, ...]
```

#### Relationships

```python
post.author                 # belongs_to -> Optional[User]
post.comments               # has_many   -> List[Comment]
user.profile                # has_one    -> Optional[Profile]
```

> ⚠️ **Honest note:** `belongs_to_many` (many-to-many relationships through a pivot table) is currently **not implemented** and will raise `NotImplementedError` if called. Use a manual query via `DB` or `RawQueryBuilder` as a temporary workaround.

### Model Observers

Observers separate lifecycle logic (what happens when a model is created, updated, deleted, etc.) from the Model class itself.

```bash
python artisan.py make:observer PostObserver --model Post
```

```python
# app/Observers/PostObserver.py
from app.Models.Post import Post
from laraflask.orm.observer import Observer


class PostObserver(Observer):
    def created(self, model: Post) -> None:
        send_new_post_notification(model)

    def updated(self, model: Post) -> None:
        clear_post_cache(model.id)

    def deleted(self, model: Post) -> None:
        cleanup_post_assets(model)
```

```python
# Register it (e.g. in a ServiceProvider.boot())
Post.observe(PostObserver)
```

**Available hooks:** `creating`, `created`, `updating`, `updated`, `deleting`, `deleted`, `saving`, `saved`, `restoring`, `restored`.

> ⚠️ **Honest note:** `Model.observe()` wires an Observer's hooks to the existing `ModelCreating`/`ModelCreated`/etc. events in `laraflask.events.dispatcher`, but those events are **still not automatically dispatched** from `Model.save()`/`delete()`. For now, you need to dispatch them manually for the observer to fire:
> ```python
> from laraflask.events.dispatcher import Events, ModelCreating, ModelCreated
>
> post = Post(title='Hello')
> Events.dispatch(ModelCreating(post))
> post.save()
> Events.dispatch(ModelCreated(post))   # PostObserver.created() fires here
> ```

### Collection

`QueryBuilder.get()` and `Model.all()` still return a plain Python `list` by default (backward compatible). Pass `as_collection=True` to get results back as a chainable `Collection` — inspired by `Illuminate\Support\Collection`.

```python
from laraflask.core.collection import Collection

posts = Post.all(as_collection=True)

posts.map(lambda p: p.title.upper()) \
     .filter(lambda p: p.published) \
     .sort_by('created_at') \
     .pluck('title') \
     .to_list()

# Available methods:
Collection([1, 2, 3]).map(lambda x: x * 2)
Collection([1, 2, 3]).filter(lambda x: x > 1)
Collection([1, 2, 3]).reduce(lambda carry, x: carry + x, 0)
Collection([1, 2, 3]).each(lambda x: print(x))
Collection([{'name': 'Rio'}]).pluck('name')
Collection([{'role': 'admin'}, {'role': 'user'}]).group_by('role')
Collection([3, 1, 2]).sort_by(lambda x: x)
Collection([1, 2, 3, 4, 5]).chunk(2)
Collection([[1, 2], [3, [4, 5]]]).flatten()
Collection([1, 1, 2, 3]).unique()
Collection([1, 2, 3]).contains(2)
Collection([1, 2, 3]).first()
Collection([1, 2, 3]).last()
Collection([1, 2, 3]).sum()
Collection([1, 2, 3]).avg()
Collection([1, 2, 3]).count()
Collection([1, 2, 3]).tap(lambda c: print(c.to_list()))   # side effect without altering the chain
Collection([1, 2, 3]).pipe(lambda c: c.sum())              # transforms the chain
Collection([1, 2, 3]).when(True, lambda c: c.map(lambda x: x * 10))
```

Additional constructors:

```python
Collection.make([1, 2, 3])
Collection.times(5, lambda n: n * 10)   # [10, 20, 30, 40, 50]
Collection.range(1, 5)                  # [1, 2, 3, 4, 5]
```

### Migrations & Schema

```python
# database/migrations/2024_01_01_000000_create_posts_table.py
from laraflask.orm.migration import Migration, Schema


class Migration_Posts(Migration):
    def up(self):
        Schema.create('posts', lambda table: [
            table.id(),
            table.string('title'),
            table.text('body'),
            table.foreign_id('user_id').references('users', 'id'),
            table.boolean('published').default(False),
            table.json('metadata').nullable(),
            table.timestamps(),
            table.soft_deletes(),
        ])

    def down(self):
        Schema.drop_if_exists('posts')
```

**Column types available on `Blueprint`:** `id()`, `integer()`, `big_integer()`, `small_integer()`, `string()`, `text()`, `boolean()`, `float_()`, `decimal()`, `date()`, `datetime()`, `timestamp()`, `json()`, `binary()`, `foreign_id()`, `vector()` (see [Vector Similarity Search](#vector-similarity-search-pgvector)), `timestamps()`, `soft_deletes()`.

**Column modifiers (chainable):** `.nullable()`, `.default(value)`, `.unique()`, `.unsigned()`, `.comment()`.

**Other Schema operations:**

```python
Schema.table('posts', lambda table: [table.string('slug').nullable()])  # add a column
Schema.drop('posts')
Schema.drop_if_exists('posts')
Schema.rename('posts', 'articles')
Schema.has_table('posts')
Schema.has_column('posts', 'slug')
Schema.enable_pgvector()   # run once before using vector columns
```

### Vector Similarity Search (pgvector)

For semantic (embedding-based) search on PostgreSQL via [pgvector](https://github.com/pgvector/pgvector):

```bash
pip install laraflask-core[vector]
```

```python
# Migration
Schema.enable_pgvector()   # CREATE EXTENSION IF NOT EXISTS vector

Schema.create('documents', lambda table: [
    table.id(),
    table.string('title'),
    table.vector('embedding', dimensions=1536),   # default 1536 (matches OpenAI text-embedding-3-small)
])
```

```python
# Query — find documents most similar to an embedding vector
from app.Models.Document import Document

query_vector = get_embedding("how to build an API with Flask")  # from your embedding provider of choice

results = (Document.query()
           .order_by_similarity('embedding', query_vector, limit=5, metric='cosine')
           .get())
```

Supported `metric` values: `'cosine'` (default — suited for normalized embeddings), `'l2'` (Euclidean), `'inner_product'`.

`order_by_similarity()` automatically sets `limit()` to the `limit` parameter unless one was already set explicitly, and can still be combined with other `.where()` calls:

```python
(Document.query()
 .where('category', 'tutorial')
 .order_by_similarity('embedding', query_vector, limit=10)
 .get())
```

## Validation (Validator & FormRequest)

### Using the Validator Directly

```python
from laraflask.validation.validator import Validator

validator = Validator(data, {
    'email': 'required|email|unique:users',
    'name': 'required|string|min:2|max:100',
    'age': 'required|integer|min:18',
    'role': 'nullable|string',
})

if validator.fails():
    return validator.errors()
    # {'email': ['The email field is required.'], ...}

validated = validator.validate()   # raises ValidationException on failure, otherwise returns valid data
```

### Available Validation Rules

| Rule | Description |
|---|---|
| `required` | Field must be present |
| `nullable` | Field may be `None` (skips other rules when empty) |
| `sometimes` | Only validates if the field is present in the data |
| `string` | Must be a string |
| `integer` | Must be castable to int |
| `numeric` | Must be castable to float |
| `boolean` | Must be a boolean-like value |
| `array` | Must be a list/tuple |
| `email` | Must be a valid email format |
| `url` | Must be a valid URL format |
| `min:N` | Minimum length/value/item count |
| `max:N` | Maximum length/value/item count |
| `unique:table,column,except_id,id_column` | Value must be unique in the table |
| `exists:table,column` | Value must exist in the table |
| `date` | Must be a valid ISO date format |
| `before:date` | Date must be before the given value |
| `after:date` | Date must be after the given value |
| `file` | Must be an uploaded file |
| `image` | Must be an image file (jpg/png/gif/bmp/svg/webp) |
| `mimes:jpg,png,pdf` | Must have one of the given file extensions |
| `json` | Must be a valid JSON string |
| `ip` | Must be a valid IP address |
| `uuid` | Must be a valid UUID |
| `required_if:field,value` | Required if another field has a given value |
| `required_unless:field,value` | Required unless another field has a given value |
| `required_with:field1,field2` | Required if any of the other fields are present |
| `prohibited` | Field must not be present |

### Custom Messages & Attribute Names

```python
validator = Validator(data, rules, messages={
    'email.required': 'The email address is required.',
    'min': 'The :attribute value is too short.',
}, attributes={
    'email': 'email address',
})
```

### Custom Rules

```python
Validator.extend('phone_id', lambda field, value, params: (
    bool(re.match(r'^08\d{8,11}$', str(value))),
    'The :attribute must be a valid Indonesian phone number.'
))

# Use it like any other rule
Validator(data, {'phone': 'required|phone_id'})
```

For a more organized, reusable rule, generate a class that wraps this same `Validator.extend()` pattern:

```bash
python artisan.py make:rule PhoneIdRule
```

```python
# app/Rules/PhoneIdRule.py
from laraflask.validation.validator import Validator


class PhoneIdRule:
    rule_name = 'phone_id_rule'

    @classmethod
    def register(cls) -> None:
        Validator.extend(cls.rule_name, cls.validate)

    @staticmethod
    def validate(field: str, value, params) -> tuple:
        passed = bool(re.match(r'^08\d{8,11}$', str(value)))
        return passed, f"The {field} field must be a valid Indonesian phone number."
```

```python
# Register once, e.g. in a ServiceProvider.boot()
PhoneIdRule.register()

# Then use it like any other rule
Validator(data, {'phone': 'required|phone_id_rule'})
```

### Conditional Rules & After Hook

```python
validator.sometimes('company_name', 'required|string', callback=lambda data: data.get('is_business'))
validator.after(lambda v: v._errors.setdefault('custom', []).append('Additional error') if some_condition else None)
```

### FormRequest

```bash
python artisan.py make:request StorePostRequest
```

```python
# app/Requests/StorePostRequest.py
from laraflask.validation.validator import FormRequest


class StorePostRequest(FormRequest):
    def authorize(self) -> bool:
        from laraflask.auth.auth import Auth
        return Auth.check()

    def rules(self) -> dict:
        return {
            'title': 'required|string|max:255',
            'body': 'required|string',
            'category_id': 'required|integer|exists:categories,id',
        }

    def messages(self) -> dict:
        return {'title.required': 'The title field is required.'}
```

```python
# In a Controller
def store(self):
    data = StorePostRequest().validate()       # 403 if authorize() is False, ValidationException on failure
    # or
    request = StorePostRequest()
    validated = request.validated()
    errors = request.errors()
```

## Authentication (Auth)

Laraflask supports 3 guards: **session** (web), **JWT** (stateless API), and **API key**.

### Guard Configuration

```python
# config/auth.py
config = {
    'defaults': {'guard': 'web'},
    'guards': {
        'web': {'driver': 'session', 'provider': 'users'},
        'api': {'driver': 'jwt', 'provider': 'users', 'ttl': 60},
    },
    'providers': {
        'users': {'driver': 'eloquent', 'model': 'app.Models.User.User'},
    },
}
```

### Login / Logout (Session Guard)

```python
from laraflask.auth.auth import Auth

if Auth.attempt({'email': email, 'password': password}):
    return redirect('/dashboard')

Auth.attempt({'email': email, 'password': password}, remember=True)  # "remember me"
Auth.login(user)                 # log in manually without checking a password
Auth.login_using_id(user_id)
Auth.logout()

Auth.user()                      # the current User, or None
Auth.check()                     # True if logged in
Auth.guest()                     # True if not logged in
Auth.id()                        # the current user's ID
```

### JWT Guard (API)

```python
guard = Auth.guard('api')
token = guard.attempt({'email': email, 'password': password})   # returns a JWT string or None

# On subsequent requests, send the header: Authorization: Bearer <token>
user = guard.user()    # automatically decoded from the header
```

### Password Hashing

```python
from laraflask.auth.auth import Hash

hashed = Hash.make('secret123')          # bcrypt (falls back to salted sha256 if bcrypt isn't installed)
Hash.check('secret123', hashed)          # True
Hash.needs_rehash(hashed, rounds=12)
```

> 💡 Passwords are hashed automatically via the `set_password_attribute` mutator on the built-in `User` model — you don't need to call `Hash.make()` manually when creating a new user.

### Auth Middleware

```python
Route.get('/dashboard', '...').middleware('auth')   # AuthMiddleware
Route.get('/login', '...').middleware('guest')      # GuestMiddleware (redirects if already logged in)
```

### Route Decorators

```python
from laraflask.auth.auth import auth_required, can

@auth_required()
def dashboard():
    ...

@auth_required(guard='api')
def api_profile():
    ...

@can('update', model_arg='post')
def update_post(post):
    ...
```

---

## Authorization (Gate & Policy)

### Gate — Simple Abilities

```python
from laraflask.auth.auth import Gate

Gate.define('edit-settings', lambda user: user.is_admin())
Gate.define('view-post', lambda user, post: post.published or post.user_id == user.id)

Gate.allows('edit-settings')              # bool, checks the currently logged-in user
Gate.denies('edit-settings')
Gate.authorize('edit-settings')           # automatically aborts(403) if denied
Gate.can('view-post', post)               # alias for allows()
Gate.for_user(other_user).can('edit-settings')  # check for a specific user (not the logged-in one)
```

### Before/After Hooks (e.g. super-admin bypass)

```python
Gate.before(lambda user, ability: True if user.is_super_admin() else None)
Gate.after(lambda user, ability, result: log_authorization(user, ability, result))
```

### Policy — Per-Model Authorization

```bash
python artisan.py make:policy PostPolicy --model Post
```

```python
# app/Policies/PostPolicy.py
from laraflask.auth.auth import Policy


class PostPolicy(Policy):
    def view(self, user, post):
        return post.published or post.user_id == user.id

    def update(self, user, post):
        return user.id == post.user_id or user.is_admin()

    def delete(self, user, post):
        return user.id == post.user_id or user.is_admin()
```

```python
# Registration (usually in AuthServiceProvider)
Gate.policy(Post, PostPolicy)

# Usage
Gate.allows('update', post)    # automatically looks up PostPolicy.update()
```

## Middleware

### Built-in Middleware

| Middleware | Alias | Description |
|---|---|---|
| `AuthMiddleware` | `auth` | Requires login, redirects/401s if not logged in |
| `GuestMiddleware` | `guest` | Only for users who aren't logged in |
| `CsrfMiddleware` | `csrf` | Verifies the CSRF token (form/header) |
| `PreventRequestForgeryMiddleware` | — | CSRF + origin-aware verification (see [Security](#security-csrf-xss-encryption)) |
| `ThrottleMiddleware` | `throttle:60,1` | Rate limiting (60 requests per 1 minute) |
| `CorsMiddleware` | `cors` | CORS headers |
| `SecureHeadersMiddleware` | — | Security headers (X-Frame-Options, etc.) |
| `TrimStringsMiddleware` | — | Automatically trims whitespace from input |
| `ConvertEmptyStringsToNullMiddleware` | — | Converts empty strings to `None` |
| `SessionMiddleware` | `session` | Initializes the session |
| `LogRequestMiddleware` | — | Logs every request |
| `ForceHttpsMiddleware` | — | Redirects HTTP → HTTPS |
| `MaintenanceModeMiddleware` | — | Maintenance mode |
| `SubstituteBindingsMiddleware` | — | Resolves models from route parameters |
| `VerifySignedMiddleware` | — | Verifies signed URLs |

### Building a Custom Middleware

```python
# app/Middleware/EnsureUserIsAdmin.py
from laraflask.middleware.middleware import Middleware


class EnsureUserIsAdmin(Middleware):
    def handle(self, request, next):
        from laraflask.auth.auth import Auth
        from flask import abort          # abort() is a Werkzeug/Flask helper — use inline only inside handle()
        user = Auth.user()
        if not user or not user.is_admin():
            abort(403)
        return next(request)
```

```python
# Register an alias in RouteServiceProvider / bootstrap
router.alias_middleware('admin', EnsureUserIsAdmin)

# Use it on a route
Route.get('/admin', '...').middleware('admin')
```

---

## Security (CSRF, XSS, Encryption)

### CSRF — Token-based (default)

```python
from laraflask.security.security import CsrfToken

token = CsrfToken.generate(session)
CsrfToken.verify(token, session)
CsrfToken.regenerate(session)   # call after login to prevent session fixation
```

In templates, include the token via the `@csrf` directive (see [Template Engine](#template-engine-bladepy)).

### CSRF + Origin-Aware Verification (`PreventRequestForgery`)

An extra layer on top of regular token-based CSRF — verifies the `Origin`/`Referer` header against a list of trusted hosts. **Optional** — the old `CsrfMiddleware` remains the default and is unaffected.

```python
from laraflask.security.security import PreventRequestForgery

guard = PreventRequestForgery(trusted_origins=['myapp.com', '*.myapp.com'])
guard.verify(token, session, request)   # True only if both the token AND the origin are valid
```

```python
# Use it as a middleware (an alternative to CsrfMiddleware)
from laraflask.middleware.middleware import PreventRequestForgeryMiddleware

router.alias_middleware('csrf-strict', PreventRequestForgeryMiddleware(trusted_origins=['myapp.com']))
```

### XSS Prevention

```python
from laraflask.security.security import XSS

XSS.clean(user_input)              # strips <script> tags, event handlers, javascript: URIs
XSS.escape(user_input)              # HTML-escape
XSS.sanitize_url(url)                # blocks javascript:/data: URIs
XSS.strip_tags(html, allowed=['p', 'b'])
```

### SQL Injection Heuristic Check

```python
from laraflask.security.security import SqlSafe

SqlSafe.is_suspicious(user_input)   # heuristic check (parameterized queries remain the primary defense)
SqlSafe.quote(value)
```

> ⚠️ EloquentPy/QueryBuilder already uses parameterized queries by default — `SqlSafe` is only relevant for manual raw SQL.

### Encryption (AES-256-CBC)

```python
from laraflask.security.security import Crypt

crypt = Crypt()   # uses APP_KEY from .env
encrypted = crypt.encrypt({'user_id': 1, 'role': 'admin'})
data = crypt.decrypt(encrypted)

crypt.encrypt_string('secret')
crypt.decrypt_string(encrypted_string)
```

> Requires `pip install cryptography` for real AES encryption — without it, falls back to simple XOR (**not safe for production**).

### Password Policy

```python
from laraflask.security.security import PasswordPolicy

policy = PasswordPolicy(min_length=8, require_uppercase=True, require_numbers=True)
policy.validate('weak')             # ['Password must be at least 8 characters.', ...]
policy.passes('Str0ngPass!')        # True
policy.strength_score('Str0ngPass!')   # 0-5
policy.strength_label('Str0ngPass!')   # 'Strong'
```

### Signed URLs

```python
from laraflask.security.security import SignedUrl

signer = SignedUrl()
url = signer.create('/verify-email/123', expiry=3600)
signer.verify(url)   # False if expired or the signature doesn't match
```

## Cache

### Available Drivers

`file` (default), `redis`, `database`, `array` (in-memory, for testing).

```python
# config/cache.py
config = {
    'default': 'file',
    'stores': {
        'file':     {'driver': 'file', 'path': 'storage/cache/data'},
        'redis':    {'driver': 'redis', 'host': '127.0.0.1', 'port': 6379, 'database': 1},
        'array':    {'driver': 'array'},
        'database': {'driver': 'database', 'table': 'cache'},
    },
}
```

### Usage

```python
from laraflask.cache.cache import Cache

Cache.put('key', 'value', seconds=3600)
Cache.get('key')
Cache.get('key', default='fallback')
Cache.has('key')
Cache.forget('key')
Cache.flush()

Cache.remember('expensive_key', 3600, lambda: compute_expensive_value())
Cache.remember_forever('static_key', lambda: compute_value())

Cache.increment('visits')
Cache.decrement('stock', 5)

# Extend the TTL without re-fetching the value — a single round-trip to the backend
Cache.touch('session:abc', 9999)
```

> `Cache.touch()` is a native single round-trip on Redis (`EXPIRE`); a metadata-only update (no value unpickling) on the File/Array/Database drivers; a custom driver that doesn't override `touch()` automatically falls back to get+put.

### Tagged Cache

```python
Cache.tags(['posts', 'user:1']).put('post:1', data, seconds=3600)
Cache.tags(['posts']).flush()   # remove every entry tagged 'posts'
```

---

## Events & Listeners

### Defining an Event

```python
# app/Events/PostPublished.py
from laraflask.events.dispatcher import Event


class PostPublished(Event):
    def __init__(self, post):
        self.post = post
```

### Listener

```python
# app/Listeners/SendPostPublishedNotification.py
from laraflask.events.dispatcher import Listener


class SendPostPublishedNotification(Listener):
    def handle(self, event):
        for subscriber in event.post.author.subscribers:
            subscriber.notify(PostPublishedNotification(event.post))
```

### Registration (EventServiceProvider)

```python
# app/Providers/EventServiceProvider.py
from laraflask.events.dispatcher import Events

class EventServiceProvider(ServiceProvider):
    def boot(self):
        Events.listen(PostPublished, SendPostPublishedNotification)
```

### Dispatching

```python
Events.dispatch(PostPublished(post))
```

### Built-in Framework Events

`RequestReceived`, `ResponseSent`, `ModelCreating`/`ModelCreated`, `ModelUpdating`/`ModelUpdated`, `ModelDeleting`/`ModelDeleted`, `ModelSaving`/`ModelSaved`, `UserRegistered`, `UserLoggedIn`, `UserLoggedOut`, `JobProcessing`/`JobProcessed`/`JobFailed`, `MessageSending`/`MessageSent`.

> ⚠️ **Honest note:** Model lifecycle events (`ModelCreating`, `ModelCreated`, etc.) are already defined as classes, but are **not yet automatically dispatched** from `Model.save()`/`delete()`. For now, you need to dispatch them manually if you need this behavior:
> ```python
> Events.dispatch(ModelCreating(post))
> post.save()
> Events.dispatch(ModelCreated(post))
> ```

### Event Subscribers (combine many listeners in a single class)

```python
from laraflask.events.dispatcher import EventSubscriber

class UserEventSubscriber(EventSubscriber):
    def subscribe(self, events):
        events.listen(UserRegistered, self.on_registered)
        events.listen(UserLoggedIn, self.on_login)

    def on_registered(self, event): ...
    def on_login(self, event): ...
```

---

## Queue & Jobs

### Defining a Job

```python
# app/Jobs/SendInvoiceEmail.py
from laraflask.queue.queue import Job


class SendInvoiceEmail(Job):
    queue = 'emails'
    tries = 3
    backoff = 30   # seconds, delay before retrying

    def __init__(self, invoice_id):
        self.invoice_id = invoice_id

    def handle(self):
        invoice = Invoice.find(self.invoice_id)
        # ... send the email

    def failed(self, exception):
        # called after all attempts have failed
        logger.error(f"Failed to send invoice: {exception}")
```

### Dispatching

```python
from laraflask.queue.queue import Queue

Queue.dispatch(SendInvoiceEmail(invoice_id=1))
Queue.push(SendInvoiceEmail(invoice_id=1), queue='emails', delay=0)
Queue.later(60, SendInvoiceEmail(invoice_id=1))   # 60-second delay
```

### Job Routing (Centralized Connection/Queue)

Register the default connection/queue for a Job class once, typically in `QueueServiceProvider.boot()` — so `dispatch()` calls don't need to repeat the configuration every time:

```python
from laraflask.queue.queue import Queue

Queue.route(SendInvoiceEmail, connection='redis', queue='high')

# dispatch() now automatically uses the 'redis' connection and 'high' queue
Queue.dispatch(SendInvoiceEmail(invoice_id=1))
```

> If a job instance already has `self.queue` explicitly overridden (the old way), that value still takes priority over the result of `route()` — 100% backward compatible.

### Worker

```bash
python artisan.py queue:work
python artisan.py queue:work --queue=emails --sleep=3 --max-jobs=100
python artisan.py queue:listen
```

### Interruptible Jobs (`Interruptible`)

The Worker gracefully catches `SIGTERM`/`SIGINT`. If the currently-running job inherits from `Interruptible`, its `interrupted()` method is called before the worker actually shuts down — a chance to save progress or release a lock.

```python
from laraflask.queue.queue import Job, Interruptible


class ProcessLargeVideo(Job, Interruptible):
    def handle(self):
        self.lock = acquire_lock(self.video_id)
        for chunk in self.chunks:
            process_chunk(chunk)
            save_progress(self.video_id, chunk.index)

    def interrupted(self, signal):
        release_lock(self.lock)
        logger.info(f"Job interrupted by signal {signal}, progress already saved")
```

### Queue Drivers

`sync` (immediate execution, for development/testing), `database`, `redis`.

> ⚠️ **Honest note:** Job chaining (`Bus.chain(...)`) and job batching (`Bus.batch(...).then(...).catch(...)`), which were once planned, are **not yet implemented** in the current codebase.

## Task Scheduler

A cron replacement defined directly in Python code, similar to `app/Console/Kernel.php` in Laravel.

```python
# app/Console/kernel.py (or routes/console.py)
from laraflask.scheduler.schedule import Schedule

Schedule.command('emails:send').daily_at('09:00')
Schedule.call(lambda: cleanup_old_sessions()).hourly()
Schedule.job(GenerateDailyReport()).daily_at('23:30').timezone('Asia/Jakarta')
```

### Available Frequencies

```python
schedule = Schedule.command('report:generate')

schedule.every_minute()
schedule.every_two_minutes()
schedule.every_five_minutes()
schedule.every_ten_minutes()
schedule.every_fifteen_minutes()
schedule.every_thirty_minutes()

schedule.hourly()
schedule.hourly_at(30)
schedule.every_two_hours()
schedule.every_three_hours()
schedule.every_six_hours()

schedule.daily()
schedule.daily_at('13:00')
schedule.twice_daily(1, 13)

schedule.weekly()
schedule.weekly_on(1, '8:00')

schedule.monthly()
schedule.monthly_on(1, '0:0')

schedule.quarterly()
schedule.yearly()
schedule.yearly_on(1, 1, '0:0')

schedule.cron('*/5 * * * *')   # custom cron expression
```

### Day Filters

```python
schedule.weekdays()
schedule.weekends()
schedule.sundays()
schedule.mondays()
schedule.tuesdays()
schedule.wednesdays()
schedule.thursdays()
schedule.fridays()
schedule.saturdays()
```

### Execution Control

```python
Schedule.command('report:generate') \
    .daily() \
    .timezone('Asia/Jakarta') \
    .without_overlapping() \
    .run_in_background() \
    .even_in_maintenance_mode() \
    .when(lambda: is_business_day()) \
    .description('Generate the daily report') \
    .send_output_to('storage/logs/report.log')
```

### Running the Scheduler

```bash
python artisan.py schedule:run     # run by the system cron every minute
python artisan.py schedule:work     # daemon mode — a cron alternative for development
```

---

## Notifications

### Available Channels

`mail`, `sms` (Twilio), `telegram`, `whatsapp` (Twilio), `database`, `push` (FCM).

### Defining a Notification

```python
# app/Notifications/InvoicePaid.py
from laraflask.notifications.notification import Notification, MailMessage, TelegramMessage


class InvoicePaid(Notification):
    def __init__(self, invoice):
        self.invoice = invoice

    def via(self, notifiable) -> list:
        return ['mail', 'database']

    def to_mail(self, notifiable) -> MailMessage:
        return (MailMessage()
                .subject('Invoice Paid')
                .greeting(f'Hello {notifiable.name},')
                .line(f'Invoice #{self.invoice.id} has been paid.')
                .action('View Invoice', f'/invoices/{self.invoice.id}')
                .success())

    def to_array(self, notifiable) -> dict:
        return {'invoice_id': self.invoice.id, 'amount': self.invoice.amount}
```

### Sending Notifications

```python
# Via a model that uses the Notifiable mixin
class User(Model, Notifiable):
    ...

user.notify(InvoicePaid(invoice))
user.notify_now(InvoicePaid(invoice))   # immediately, bypassing the queue

# Via the global facade
from laraflask.notifications.notification import Notification_
Notification_.send(user, InvoicePaid(invoice))
Notification_.send([user1, user2], InvoicePaid(invoice))   # multiple recipients

# Notify an anonymous recipient (no Model)
Notification_.route('mail', 'someone@example.com').notify(InvoicePaid(invoice))
```

### Managing Database Notifications

```python
user.unread_notifications()
user.read_notifications()
user.mark_all_as_read()
```

### MailMessage — Fluent Builder

```python
MailMessage() \
    .subject('Email Subject') \
    .greeting('Hello!') \
    .line('First line.') \
    .line('Second line.') \
    .action('Click Here', 'https://example.com') \
    .salutation('Regards,\nThe Laraflask Team') \
    .attach('/path/to/file.pdf') \
    .success()   # styling level: success/error/warning
```

---

## Storage / Filesystem

### Drivers

`local` (default), `s3` (AWS S3 / S3-compatible: MinIO, Cloudflare R2).

```python
# config/storage.py
config = {
    'default': 'local',
    'disks': {
        'local':  {'driver': 'local', 'root': 'storage/app', 'url': '/storage'},
        'public': {'driver': 'local', 'root': 'storage/app/public', 'visibility': 'public'},
        's3':     {'driver': 's3', 'key': '...', 'secret': '...', 'bucket': '...', 'region': 'us-east-1'},
    },
}
```

### Usage

```python
from laraflask.storage.storage import Storage

Storage.put('avatars/user1.jpg', file_contents)
Storage.put_file('avatars', uploaded_file)            # auto-generates the file name
Storage.put_file_as('avatars', uploaded_file, 'user1.jpg')

Storage.get('avatars/user1.jpg')          # bytes
Storage.get_string('config.json')         # str
Storage.exists('avatars/user1.jpg')
Storage.missing('avatars/user1.jpg')

Storage.delete('avatars/user1.jpg')
Storage.copy('a.jpg', 'b.jpg')
Storage.move('a.jpg', 'b.jpg')

Storage.size('avatars/user1.jpg')
Storage.url('avatars/user1.jpg')
Storage.temporary_url('avatars/user1.jpg', expiry=3600)   # temporary signed URL

Storage.files('avatars')                # list files (non-recursive)
Storage.all_files('avatars')            # list files (recursive)
Storage.directories('avatars')
Storage.make_directory('new-folder')
Storage.delete_directory('old-folder')

Storage.disk('s3').put('backups/db.sql', data)   # use a specific disk
```

## Template Engine (BladePy)

A Blade-style template engine, compiled down to Jinja2 (so every Jinja2 feature is still available). Template files use the `.blade.html` extension and live in `resources/views/`.

```html
<!-- resources/views/layouts/app.blade.html -->
<!DOCTYPE html>
<html>
<head><title>@yield('title', 'Laraflask')</title></head>
<body>
    @include('partials.navbar')
    @yield('content')
</body>
</html>
```

```html
<!-- resources/views/posts/show.blade.html -->
@extends('layouts.app')

@section('title', $post['title'])

@section('content')
    <h1>{{ $post['title'] }}</h1>
    <p>{!! $post['body_html'] !!}</p>   {{-- unescaped output --}}

    @auth
        <a href="/posts/{{ $post['id'] }}/edit">Edit</a>
    @endauth

    @can('delete', $post)
        <button>Delete</button>
    @endcan

    @foreach ($comments as $comment)
        <p>{{ $comment['body'] }}</p>
    @endforeach

    @forelse ($related as $item)
        <li>{{ $item['title'] }}</li>
    @empty
        <p>No related articles.</p>
    @endforelse

    <form method="POST" action="/posts/{{ $post['id'] }}">
        @csrf
        @method('PUT')
        <button type="submit">Save</button>
    </form>
@endsection
```

### Available Directives

`@extends`, `@section`/`@endsection`, `@yield`, `@include`, `@if`/`@elseif`/`@else`/`@endif`, `@unless`/`@endunless`, `@foreach`/`@endforeach`, `@for`/`@endfor`, `@while`/`@endwhile`, `@forelse`/`@empty`/`@endforelse`, `@switch`/`@case`/`@break`/`@default`/`@endswitch`, `@csrf`, `@method`, `@auth`/`@endauth`, `@guest`/`@endguest`, `@can`/`@endcan`, `@cannot`/`@endcannot`, `@env`/`@endenv`, `@production`/`@endproduction`, `@push`/`@endpush`, `@stack`, `@once`/`@endonce`, `@verbatim`/`@endverbatim`, `@dump`, `@dd`, `@php`/`@endphp`, `@json`, `@class`, `@style`, `@checked`, `@selected`, `@disabled`, `@required`, `@error`/`@enderror`.

### Rendering from a Controller

```python
def show(self, id):
    post = Post.find_or_fail(id)
    # Use self.view() from Controller base class (calls render_template internally)
    return self.view('posts.show', {'post': post.to_dict()})
```

---

## API Resource & JSON:API

### ApiResponse — Consistent Response Format

```python
from laraflask.api.api import ApiResponse

ApiResponse.success(data, message='OK', status=200)
ApiResponse.error(message='Not Found', status=404)
ApiResponse.paginated(items, total=100, per_page=15, page=1)
```

### ApiResource — Simple Transformer

```bash
python artisan.py make:resource PostResource
```

```python
from laraflask.api.api import ApiResource

class PostResource(ApiResource):
    def to_array(self) -> dict:
        # self._resource holds the model/object passed into the constructor.
        return {
            'id': self._resource.id,
            'title': self._resource.title,
            'author': self._resource.author.name,
        }

PostResource(post).to_response()
PostResource.collection(posts).to_response()
```

### JsonApiResource — [JSON:API](https://jsonapi.org/format/) Specification

For APIs that follow the full JSON:API standard: the `{data, included, links, meta}` structure, sparse fieldsets, and relationship inclusion.

```bash
python artisan.py make:resource PostResource --jsonapi
```

```python
from laraflask.api.jsonapi import JsonApiResource

class PostResource(JsonApiResource):
    type_ = 'posts'

    def attributes(self) -> dict:
        return {'title': self.model.title, 'body': self.model.body}

    def relationships(self) -> dict:
        return {'author': self.model.author, 'comments': self.model.comments}

    def resource_class_for(self, relation_name, related_model):
        if relation_name == 'author':
            return UserResource
        if relation_name == 'comments':
            return CommentResource
        return JsonApiResource
```

```python
# Single resource
PostResource(post).to_response()
# -> {"data": {"type": "posts", "id": "1", "attributes": {...}, "relationships": {...}}}

# Collection
PostResource.collection(posts).to_response()
# -> {"data": [...], "included": [...]}  (included is automatically deduplicated across items)
```

**Sparse Fieldsets** (`?fields[posts]=title`):

```
GET /api/posts/1?fields[posts]=title
```
Only the `title` field appears in `attributes`.

**Relationship Inclusion** (`?include=author,comments`):

```
GET /api/posts/1?include=author,comments
```
The full `author` and `comments` resources are automatically added to the `included` member.

```python
# Response with extra meta & links
PostResource(post).to_response(
    meta={'request_id': 'abc-123'},
    links={'self': '/api/posts/1'},
)
```

### Rate Limiting (`RateLimiter`)

```python
from laraflask.api.api import RateLimiter

RateLimiter.attempt(key=f'login:{ip_address}', max_attempts=5, decay_seconds=60)  # bool
RateLimiter.too_many_attempts(key, max_attempts=5)
RateLimiter.available_in(key)        # seconds remaining until reset
RateLimiter.remaining_attempts(key, max_attempts=5)
RateLimiter.clear(key)

RateLimiter.for_('uploads', lambda request: RateLimiter.attempt(f'upload:{request.remote_addr}', 10, 60))
```

Or via middleware: `Route.get('/api/data', '...').middleware('throttle:60,1')` (60 requests per 1 minute).

### OpenAPI Generator & Swagger UI

```python
from laraflask.api.api import OpenApiGenerator

spec = OpenApiGenerator(title='My API', version='1.0.0', description='My API documentation')

spec.add_path('/posts', 'GET', summary='List all posts', tags=['Posts'])
spec.add_path('/posts/{id}', 'GET', summary='Get a single post', tags=['Posts'])
spec.add_schema('Post', {'type': 'object', 'properties': {'id': {'type': 'integer'}}})
spec.server('https://api.myapp.com', description='Production')

spec.to_dict()    # the OpenAPI 3.0 spec as a dict
spec.to_json()

# Automatically registers /api/openapi.json and /api/docs (Swagger UI)
spec.register_routes(router, prefix='/api')
```

---

## WebSocket & Broadcasting

```bash
pip install laraflask-core[websocket]
```

### Setup

```python
from laraflask.ws.websocket import WebSocketManager

ws = WebSocketManager()
ws.init_app(flask_app)

@ws.on('chat:message')
def handle_message(data):
    ws.to('room-1').emit('chat:message', data)
```

### Broadcasting an Event

```python
from laraflask.ws.websocket import BroadcastEvent, Channel, PrivateChannel, Broadcast


class OrderShipped(BroadcastEvent):
    def __init__(self, order):
        self.order = order

    def broadcast_on(self) -> list:
        return [PrivateChannel(f'orders.{self.order.id}')]

    def broadcast_with(self) -> dict:
        return {'order_id': self.order.id, 'status': 'shipped'}


Broadcast.event(OrderShipped(order))
```

### Room Management

```python
ws.join_room('room-1', sid=request.sid)
ws.leave_room('room-1', sid=request.sid)
ws.clients_in_room('room-1')
ws.connected_count()
```

### Server-Sent Events (SSE) — A WebSocket-Free Alternative

```python
from laraflask.ws.websocket import SSEManager

sse = SSEManager()

@app.route('/stream')
def stream():
    return sse.stream(channel='notifications')

# Elsewhere (e.g. after a job finishes):
sse.publish('notifications', data=json.dumps({'message': 'Done!'}))
```

## Testing

### Unit Tests

```python
# app/tests/Unit/test_post_model.py
from laraflask.testing.test_case import UnitTestCase
from app.Models.Post import Post


class PostModelTest(UnitTestCase):
    def before_each(self):
        self.post = Post(title='Hello', body='World')

    def test_title_is_capitalized(self):
        self.assertEqual(self.post.title, 'Hello')
```

> Use `before_each()`/`after_each()` (not `setUp()`/`tearDown()` directly — both are already called automatically by `TestCase`).

### Feature Tests (HTTP)

```python
# app/tests/Feature/test_post_api.py
from laraflask.testing.test_case import FeatureTestCase
from app.Models.User import User
from app.Models.Post import Post


class PostApiTest(FeatureTestCase):
    def test_guest_cannot_create_post(self):
        response = self.post('/api/posts', {'title': 'Test'})
        response.assert_status(401)

    def test_authenticated_user_can_create_post(self):
        user = self.create(User, name='Rio', email='rio@test.com')
        response = self.acting_as(user).post('/api/posts', {
            'title': 'New Title',
            'body': 'Content body',
        })
        response.assert_created()
        self.assert_database_has('posts', {'title': 'New Title'})

    def test_api_with_jwt_token(self):
        response = self.with_token('eyJ...').get('/api/profile')
        response.assert_ok()
```

### HTTP Helpers

```python
self.get(uri, headers=...)
self.post(uri, data=...)
self.put(uri, data=...)
self.patch(uri, data=...)
self.delete(uri)
self.call(method, uri, data=...)

self.acting_as(user)              # log in as a user (session guard)
self.acting_as_api(user)          # log in as a user (JWT guard, auto-generates a token)
self.with_token(token)            # set the Authorization: Bearer <token> header
```

### Response Assertions

```python
response.assert_status(200)
response.assert_ok()                # 200
response.assert_created()           # 201
response.assert_no_content()        # 204
response.assert_not_found()         # 404
response.assert_forbidden()         # 403
response.assert_unauthorized()      # 401
response.json()
response.data
response.text
response.headers
```

### Database Assertions

```python
self.assert_database_has('posts', {'title': 'New Title'})
self.assert_database_missing('posts', {'title': 'Deleted'})
self.assert_database_count('posts', 5)
self.refresh_database()   # reset the database to a clean state
```

### Database Seeders & Factories

**Seeder** — populate the database with initial/sample data:

```bash
python artisan.py make:seeder PostSeeder
```

```python
# database/seeders/PostSeeder.py
from laraflask.orm.seeder import Seeder
from database.factories.PostFactory import PostFactory


class PostSeeder(Seeder):
    def run(self) -> None:
        PostFactory().count(20).create()
```

Run it via `python artisan.py db:seed`. A main `DatabaseSeeder` can call several seeders in sequence with `self.call(...)`:

```python
class DatabaseSeeder(Seeder):
    def run(self) -> None:
        self.call(UserSeeder, PostSeeder, CommentSeeder)
```

**Factory** — generate dummy model instances, backed by [Faker](https://faker.readthedocs.io/) (`pip install laraflask-core[testing]`):

```bash
python artisan.py make:factory PostFactory --model Post
```

```python
# database/factories/PostFactory.py
from laraflask.orm.factory import Factory
from app.Models.Post import Post


class PostFactory(Factory):
    model = Post

    def definition(self) -> dict:
        return {
            'title': self.faker.sentence(),
            'body': self.faker.paragraph(),
        }
```

| Method | Description |
|---|---|
| `.make()` | Build an instance **without** persisting it |
| `.create()` | Build an instance **and** save it to the database |
| `.count(n)` | Produce `n` instances instead of 1 (returns a list) |
| `.state(**overrides)` | Override specific attributes from `definition()`, chainable |

```python
post = PostFactory().make()                              # instance only, not saved
post = PostFactory().create()                              # instance + saved to DB
posts = PostFactory().count(10).create()                   # 10 saved instances
post = PostFactory().state(title='Pinned Post').create()   # override one field
```

> 💡 In test classes that inherit `UnitTestCase`/`FeatureTestCase`, `self.create(Model, **attrs)` / `self.make(Model, **attrs)` remain available as convenience shortcuts on top of any registered factory.

### Fakes (Isolating Side Effects)

```python
def test_publishing_post_sends_notification(self):
    events = self.fake_events()
    queue = self.fake_queue()
    notifications = self.fake_notifications()
    storage = self.fake_storage()
    mail = self.fake_mail()

    # ... run the code under test ...

    events.assert_dispatched(PostPublished)
    queue.assert_pushed(SendNewsletterJob)
    queue.assert_not_pushed(SendSpamJob)
```

### Running Tests

```bash
python -m unittest discover -s app/tests/Unit
python -m unittest discover -s app/tests/Feature
pytest app/tests/        # if pytest is installed (more features: -k, -v, etc.)
```

## Artisan CLI

Every command is run via `python artisan.py <command>` from the project root.

### Code Generation

| Command | Description |
|---|---|
| `make:model ModelName` | Create a new Model class |
| `make:controller ControllerName` | Create a new Controller class |
| `make:migration migration_name` | Create a new migration file |
| `make:middleware MiddlewareName` | Create a new Middleware class |
| `make:job JobName` | Create a new Job class |
| `make:event EventName` | Create a new Event class |
| `make:listener ListenerName` | Create a new Listener class |
| `make:notification NotificationName` | Create a new Notification class |
| `make:request RequestName` | Create a new FormRequest class in `app/Requests` |
| `make:policy PolicyName [--model ModelName]` | Create a new Policy class in `app/Policies`; with `--model`, the standard methods (`view_any`, `view`, `create`, `update`, `delete`, `restore`, `force_delete`) are type-hinted against that model |
| `make:resource ResourceName [--jsonapi]` | Create a new API resource class in `app/Resources`; defaults to `ApiResource`, or `JsonApiResource` with `--jsonapi` |
| `make:rule RuleName` | Create a new custom validation rule in `app/Rules`, ready to register via `RuleName.register()` |
| `make:provider ProviderName` | Create a new ServiceProvider class in `app/Providers` |
| `make:seeder SeederName` | Create a new database seeder in `database/seeders` |
| `make:factory FactoryName [--model ModelName]` | Create a new model factory in `database/factories`, wired to Faker |
| `make:observer ObserverName [--model ModelName]` | Create a new model observer in `app/Observers` |
| `make:command CommandName [--command-name name]` | Create a new custom Artisan command in `app/Console` |

```bash
python artisan.py make:request StorePostRequest
python artisan.py make:policy PostPolicy --model Post
python artisan.py make:resource PostResource --jsonapi
python artisan.py make:rule PhoneIdRule
python artisan.py make:provider PaymentServiceProvider
python artisan.py make:seeder PostSeeder
python artisan.py make:factory PostFactory --model Post
python artisan.py make:observer PostObserver --model Post
python artisan.py make:command SendDigestCommand --command-name digest:send
```

### Database

| Command | Description |
|---|---|
| `migrate` | Run pending migrations |
| `migrate:rollback` | Roll back the last migration batch |
| `migrate:refresh` | Reset and re-run all migrations |
| `migrate:fresh` | Drop all tables and re-run migrations |
| `migrate:status` | Show the status of every migration |
| `db:seed` | Seed the database |

### Routing

| Command | Description |
|---|---|
| `route:list` | List every registered route |

### Queue & Scheduler

| Command | Description |
|---|---|
| `queue:work` | Process jobs from the queue (`--queue=`, `--sleep=`, `--max-jobs=`) |
| `queue:listen` | Listen on a specific queue |
| `schedule:run` | Run due scheduled commands (invoked by cron every minute) |
| `schedule:work` | Run the scheduler as a daemon (a cron alternative) |

### Utilities

| Command | Description |
|---|---|
| `tinker` | Open the interactive REPL (see the [Tinker section](#tinker-interactive-repl)) |
| `cache:clear` | Clear the entire application cache |
| `serve` | Start the development server |
| `key:generate` | Generate a new `APP_KEY` |
| `env:decrypt` | Decrypt an encrypted environment file |
| `about` | Show basic application information |

```bash
python artisan.py make:model Post
python artisan.py make:controller PostController
python artisan.py make:migration create_posts_table
python artisan.py migrate
python artisan.py route:list
python artisan.py queue:work --queue=emails --sleep=3
python artisan.py serve --host=0.0.0.0 --port=8000
```

---

## Tinker (Interactive REPL)

`python artisan.py tinker` opens an interactive Python REPL with a bootstrapped `Application`, every Model from `app/Models/*.py`, and the core helpers — all automatically imported into the namespace.

```bash
$ python artisan.py tinker
Laraflask Tinker [Python 3.12.3]
14 variable(s) auto-imported. Type `dir()` to see them, `exit()` to quit.

>>> User.count()
42
>>> user = User.find(1)
>>> user.email
'rio@example.com'
>>> DB.select('SELECT COUNT(*) as total FROM posts')
[{'total': 128}]
>>> Cache.put('test', 'value', seconds=60)
>>> exit()
```

**Auto-imported into the namespace:** every `Model` class in `app/Models/`, plus `app` (the `Application` instance), `DB`, `Cache`, `Auth`, `Gate`, `Hash`, `Events`, `Queue`, `Storage`, `Schedule`, `Validator`.

If [IPython](https://ipython.org/) is installed, Tinker automatically uses it (autocomplete, syntax highlighting); otherwise, it falls back to Python's standard `code.InteractiveConsole` (with command history saved to `~/.laraflask_tinker_history`).

---

## Advanced Container (Contextual Binding & Tagging)

See also [Service Container](#application--service-container) for basic binding.

### Contextual Binding

```python
container.when(InvoiceController).needs(Logger).give(FileLogger)
container.when(PaymentController).needs(Logger).give(SentryLogger)
```

### Tagging

```python
container.tag([WeeklyReport, MonthlyReport], 'reports')
for report in container.tagged('reports'):
    report.generate()
```

---

## Macroable

A mixin that lets you add new methods to a class **dynamically at runtime** — inspired by `Illuminate\Support\Traits\Macroable`. `QueryBuilder` already inherits from `Macroable` by default.

```python
from laraflask.orm.model import QueryBuilder

QueryBuilder.macro('whereActive', lambda self: self.where('active', True))

Post.query().whereActive().get()    # the new method is immediately usable
```

### On a Custom Class

```python
from laraflask.core.macroable import Macroable

class Money(Macroable):
    def __init__(self, amount):
        self.amount = amount

Money.macro('formatted', lambda self: f"${self.amount:,}")
Money(50000).formatted()   # '$50,000'

Money.has_macro('formatted')     # True
Money.mixin(SomeHelperClass)      # register every public method at once
Money.flush_macros()               # remove every macro belonging to this class
```

> Macros are **isolated per subclass** — registering a macro on one `Macroable` class will not "leak" into another class that also inherits from `Macroable`.

---

## Exception Handling

### Built-in Framework Exceptions

```python
from laraflask.core.exceptions import (
    LaraflaskException,          # base exception
    ApplicationException,
    ModelNotFoundException,
    AuthorizationException,
    AuthenticationException,
    ValidationException,
    HttpException,
    NotFoundHttpException,        # 404
    UnauthorizedHttpException,    # 401
    ForbiddenHttpException,       # 403
    MethodNotAllowedHttpException,  # 405
    TooManyRequestsException,     # 429
    MaintenanceModeException,     # 503
    TokenMismatchException,       # 419 (CSRF)
    EncryptException,
    QueueException,
    CacheException,
    StorageException,
    NotificationException,
)
```

### Global Exception Handler

```python
# app/Exceptions/Handler.py
from laraflask.core.exceptions import ModelNotFoundException, ValidationException
from laraflask.api.api import ApiResponse


class Handler:
    def render(self, request, exception):
        if isinstance(exception, ModelNotFoundException):
            return ApiResponse.not_found()
        if isinstance(exception, ValidationException):
            return ApiResponse.validation_error(exception.errors)
        # ... default fallback
```

---

## Deployment

### Production Checklist

```bash
pip install laraflask-core[production]   # gunicorn + gevent
```

```env
APP_ENV=production
APP_DEBUG=false
APP_KEY=<result of key:generate, NEVER leave this blank>
SESSION_SECURE_COOKIE=true
```

```bash
# Run with Gunicorn (never use Flask's dev server in production)
gunicorn -w 4 -k gevent -b 0.0.0.0:8000 laraflask:flask_app
```

### Production Security Checklist

- [ ] `APP_DEBUG=false`
- [ ] `APP_KEY` is generated uniquely (`python artisan.py key:generate`), not left at a default value
- [ ] Production database uses MySQL/PostgreSQL, not SQLite
- [ ] `SESSION_SECURE_COOKIE=true` if serving over HTTPS
- [ ] Use `ForceHttpsMiddleware` behind a reverse proxy that terminates TLS
- [ ] Consider `PreventRequestForgeryMiddleware` for an extra CSRF layer on critical endpoints
- [ ] Install `cryptography` & `bcrypt` so `Crypt`/`Hash` don't fall back to their weaker substitute implementations

## Changelog

### v1.4.0 (latest)

| # | Area | File(s) | Change |
|---|---|---|---|
| 1 | Artisan generators | `console/artisan.py` | Implemented `make:request`, `make:policy`, `make:resource`, `make:rule`, `make:provider`, `make:seeder`, `make:factory`, `make:observer`, `make:command` — previously documented as not yet implemented. |
| 2 | `make:policy` / `make:observer` / `make:factory` | `console/artisan.py` | Accept `--model` to generate methods type-hinted against a specific model. |
| 3 | `make:resource` | `console/artisan.py` | Accepts `--jsonapi` to scaffold a `JsonApiResource` instead of the default `ApiResource`. |
| 4 | `Seeder` (new) | `orm/seeder.py` | Base class for database seeders, with `call()` to compose multiple seeders. |
| 5 | `Factory` (new) | `orm/factory.py` | Faker-backed base class for model factories: `make()`, `create()`, `count()`, `state()`. |
| 6 | `Observer` (new) | `orm/observer.py` | Base class for model observers with the standard lifecycle hooks. |
| 7 | `Model.observe()` | `orm/model.py` | Wires an `Observer`'s hooks to the existing `ModelCreating`/`ModelCreated`/etc. events. Those events are still not auto-dispatched from `save()`/`delete()` — see [Model Observers](#model-observers). |
| 8 | Documentation | `README.md` | Added "Model Observers" and "Database Seeders & Factories" sections; updated the Artisan CLI command table; updated "Known Limitations". |

### v1.3.0 (latest)

| # | Area | File(s) | Change |
|---|---|---|---|
| 1 | **Import hygiene — routes** | `routes/web.py`, `routes/api.py` | Removed stale `from flask import …` top-level imports. `Route` is injected by the framework; responses use `ApiResponse` from core. |
| 2 | **Import hygiene — Controller** | `app/Controllers/Controller.py` | Moved all `from flask import …` statements from module-level to lazy inline imports inside each method. `respond()` and `error()` now delegate to `ApiResponse` from core for a consistent response envelope. |
| 3 | **Import hygiene — Handler** | `app/Exceptions/Handler.py` | Removed module-level `from flask import …`. All Flask primitives (`jsonify`, `request`, `redirect`, `Response`) are now imported lazily inside each method where they are used. |
| 4 | **Import hygiene — Tests** | `tests/Unit/test_jsonapi.py`, `tests/Unit/test_prevent_request_forgery.py` | Removed top-level `from flask import Flask`. Extracted `_make_flask_app()` helper that defers the import to call-time; inline `from flask import request/session` kept inside middleware `with test_request_context` blocks where a live request context is required. |
| 5 | **Documentation — README** | `README.md` | Fixed three code examples that showed top-level Flask imports in user-space files: middleware example now uses inline `abort()`; template controller example uses `self.view()` from the base `Controller`; Handler example uses `ApiResponse.not_found()` / `ApiResponse.validation_error()`. Version updated to v1.3.0. |
| 6 | **Dependency versions** | `core/pyproject.toml`, `core/setup.py` | All optional and core dependency pins bumped to latest stable releases as of June 2026. |

### v1.2.0

| # | Area | File(s) | Change |
|---|---|---|---|
| 1 | `Cache::touch()` | `cache/cache.py` | Extend a key's TTL without re-fetching its value — a native single round-trip on Redis (`EXPIRE`), metadata-only update on File/Array/Database. |
| 2 | `Queue::route()` | `queue/queue.py` | Centrally register the default connection/queue per Job class. An explicit instance-level override still wins (backward compatible). |
| 3 | `Interruptible` | `queue/queue.py` | The `interrupted(signal)` mixin — the Worker catches SIGTERM/SIGINT and calls it before exiting. |
| 4 | JSON:API Resource | `api/jsonapi.py` (new) | `JsonApiResource`/`JsonApiResourceCollection` per the JSON:API spec: `{data, included, links, meta}`, sparse fieldsets, relationship inclusion. |
| 5 | Model decorators | `orm/model.py` | `@table`, `@hidden`, `@fillable` as an alternative to manually-declared class attributes — fully backward compatible. |
| 6 | Vector similarity search | `orm/migration.py`, `orm/model.py` | `Blueprint.vector()` + `QueryBuilder.order_by_similarity()` for pgvector (PostgreSQL). |
| 7 | `PreventRequestForgery` | `security/security.py`, `middleware/middleware.py` | An origin-aware CSRF layer on top of regular token-based CSRF — opt-in, the old `CsrfMiddleware` is unchanged. |

### v1.1.0

| # | Feature | File(s) | Description |
|---|---|---|---|
| 1 | `tinker` | `console/artisan.py` | An interactive REPL with every Model & core helper auto-imported. |
| 2 | `Collection` | `core/collection.py` (new) | A chainable wrapper inspired by `Illuminate\Support\Collection`. `as_collection=True` is opt-in on `get()`/`all()`. |
| 3 | Contextual binding & tagging | `core/container.py` | `when().needs().give()` and `tag()`/`tagged()` on the Service Container. |
| 4 | `Macroable` | `core/macroable.py` (new) | A mixin for adding methods dynamically at runtime. `QueryBuilder` inherits from this. |

### v1.0.1 — Bug Fixes

| # | File | Bug | Fix |
|---|---|---|---|
| 1 | `core/exceptions.py` | `ValidationException`/`ModelNotFoundException` were defined in 3 different places → `isinstance()` checks failed to match | Single definition in `core/exceptions.py`, every module imports from there |
| 2 | `orm/db.py` | SQLite was used with `QueuePool` + `pool_size` — SQLite doesn't support connection pooling | `StaticPool` for `:memory:`, `NullPool` for file-based SQLite; `QueuePool` is used only for MySQL/PostgreSQL |
| 3 | `orm/model.py` | `session.query(Model).get(pk)` — deprecated in SQLAlchemy 2.x | Replaced with `session.get(Model, pk)` |
| 4 | `orm/model.py` | `first_or_create`'s `.where()` result wasn't re-chained | Fixed: `query = query.where(k, v)` |
| 5 | `orm/model.py` | `ModelNotFoundException` was duplicated, shadowing the version from `core.exceptions` | Duplicate removed |
| 6 | `orm/model.py` | Soft-delete filtering used the old `_soft_delete` attribute | Fixed to use `__soft_delete__` |
| 7 | `validation/validator.py` | `ValidationException` was redefined locally | Removed, now imported from `core.exceptions` |
| 8 | `auth/auth.py` | `Hash.needs_rehash()` called `bcrypt.checkpw()` with empty bytes → `ValueError` | Fixed |
| 9 | `core/application.py` | `importlib.util` was used without being imported separately | Added `import importlib.util` |
| 10 | `scheduler/schedule.py` | `class Event` collided with `events.dispatcher.Event` | Renamed to `ScheduledEvent` |

---

## Known Limitations

This section is documented honestly so it doesn't create false expectations:

- **`belongs_to_many`** (many-to-many relationships through a pivot table) is not implemented — calling it raises `NotImplementedError`.
- **Model lifecycle events** (`ModelCreating`, `ModelCreated`, `ModelUpdating`, etc.) are already defined as Event classes, and `Model.observe()` can wire an `Observer`'s hooks to them — but the events themselves are **still not automatically dispatched** from `Model.save()`/`delete()`. They need to be dispatched manually for an Observer to actually fire; see [Model Observers](#model-observers) for the workaround.
- **Job chaining & batching** (`Bus.chain([...]).dispatch()`, `Bus.batch([...]).then().catch()`) are **not implemented**.
- **Sanctum-style API Token Auth** (`PersonalAccessToken`, `HasApiTokens`, a `TokenGuard` based on the `Authorization: Bearer` header) is **not implemented**. For stateless API authentication today, use the JWT Guard instead (see [Authentication](#authentication-auth)).
- **`Hash`/`Crypt` fallback behavior**: without `bcrypt`/`cryptography` installed, both fall back to a simpler implementation (salted SHA-256 / XOR) that is **not safe for production**. Always install `pip install laraflask-core[auth]` in production environments.
- **HTTP status 419** (CSRF token mismatch) is used by `CsrfMiddleware`/`PreventRequestForgeryMiddleware` via `abort(419)`, but 419 isn't a standard HTTP code in Werkzeug — register a custom exception handler for this code at your application level if you don't already have one, or handle it via `app.errorhandler`.

Pull requests for any of the items above are very welcome.

---

## License

MIT License.

## Contributing

Pull requests and issue reports are welcome. Please include unit tests for any new feature, and run `python -m unittest discover -s app/tests/Unit` before submitting.
