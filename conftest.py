"""
pytest configuration for Laraflask test suite.
"""

import os
import sys
import pytest

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Force testing environment
os.environ.setdefault('APP_ENV', 'testing')
os.environ.setdefault('APP_DEBUG', 'true')
os.environ.setdefault('DB_CONNECTION', 'sqlite')
os.environ.setdefault('DB_DATABASE', ':memory:')
os.environ.setdefault('CACHE_DRIVER', 'array')
os.environ.setdefault('QUEUE_CONNECTION', 'sync')
os.environ.setdefault('SESSION_DRIVER', 'filesystem')
os.environ.setdefault('APP_KEY', 'base64:test-key-for-testing-only-32bytes!!!')


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Mark test as a unit test")
    config.addinivalue_line("markers", "feature: Mark test as a feature/integration test")
    config.addinivalue_line("markers", "slow: Mark test as slow-running")
    config.addinivalue_line("markers", "db: Mark test as requiring database")


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    from laraflask.core.application import Application
    application = Application(os.path.dirname(os.path.abspath(__file__)))
    application.bootstrap()
    return application


@pytest.fixture(scope='session')
def flask_app(app):
    """Get Flask test app."""
    flask = app.get_flask()
    flask.config['TESTING'] = True
    return flask


@pytest.fixture
def client(flask_app):
    """Flask test client."""
    with flask_app.test_client() as c:
        yield c


@pytest.fixture
def runner(flask_app):
    """Flask CLI test runner."""
    return flask_app.test_cli_runner()


@pytest.fixture(autouse=True)
def reset_cache():
    """Reset cache before each test."""
    from laraflask.cache.cache import Cache
    try:
        Cache.flush()
    except Exception:
        pass
    yield
    try:
        Cache.flush()
    except Exception:
        pass


@pytest.fixture(autouse=True)
def reset_schedule():
    """Reset scheduler before each test."""
    from laraflask.scheduler.schedule import Schedule
    Schedule._events = []
    yield
    Schedule._events = []


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset rate limiter state before each test."""
    from laraflask.api.api import RateLimiter
    RateLimiter._store.clear()
    yield
    RateLimiter._store.clear()


@pytest.fixture
def fake_events():
    """Fake event dispatcher."""
    from laraflask.testing.test_case import EventFake
    from laraflask.events.dispatcher import Events
    fake = EventFake()
    original = Events._dispatcher
    Events._dispatcher = fake
    yield fake
    Events._dispatcher = original


@pytest.fixture
def fake_queue():
    """Fake queue driver."""
    from laraflask.testing.test_case import QueueFake
    from laraflask.queue.queue import Queue
    fake = QueueFake()
    original = Queue._connections.get('default')
    Queue._connections['default'] = fake
    yield fake
    if original:
        Queue._connections['default'] = original
    else:
        Queue._connections.pop('default', None)


@pytest.fixture
def fake_storage(tmp_path):
    """Fake local storage backed by tmp_path."""
    from laraflask.storage.storage import Storage, LocalDriver
    driver = LocalDriver(root=str(tmp_path))
    original = Storage._disks.get('local')
    Storage._disks['local'] = driver
    yield driver
    if original:
        Storage._disks['local'] = original
    else:
        Storage._disks.pop('local', None)


@pytest.fixture
def array_cache():
    """In-memory cache driver."""
    from laraflask.cache.cache import Cache, ArrayDriver
    driver = ArrayDriver()
    Cache._stores['array'] = driver
    Cache._default = 'array'
    yield driver
    driver.flush()
