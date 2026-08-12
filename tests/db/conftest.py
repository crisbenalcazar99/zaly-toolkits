# conftest.py — Fixtures del toolkit db.
import pytest

from zaly_toolkits.db import engine as engine_module
from zaly_toolkits.db import redis_client as redis_client_module


@pytest.fixture(autouse=True)
def _reset_engine_caches():
    """Evita que un test contamine a otro via los caches singleton de engine.py."""
    engine_module._engine_cache.clear()
    engine_module._session_cache.clear()
    yield
    engine_module._engine_cache.clear()
    engine_module._session_cache.clear()


@pytest.fixture(autouse=True)
def _reset_redis_cache():
    """Evita que un test contamine a otro via el cache singleton de redis_client.py."""
    redis_client_module._redis_cache.clear()
    yield
    redis_client_module._redis_cache.clear()


@pytest.fixture
def postgres_config():
    return {
        "engine_database": "POSTGRES",
        "host": "localhost",
        "port": 5432,
        "user": "app",
        "password": "secret",
        "db_name": "app_db",
    }


@pytest.fixture
def sqlserver_config():
    return {
        "engine_database": "SQLSERVER",
        "host": "sqlhost",
        "port": 1433,
        "odbc_driver": "ODBC Driver 17 for SQL Server",
        "user": "app",
        "password": "secret",
        "db_name": "app_db",
    }


@pytest.fixture
def redis_config():
    return {
        "engine_database": "REDIS",
        "host": "redishost",
        "port": 6379,
        "user": "app",
        "password": "secret",
        "db_index": 2,
    }