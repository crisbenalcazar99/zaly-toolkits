# redis_client.py — Crea y cachea clientes redis-py por alias.
#
# Mismo patron de singleton por alias que engine.py, pero Redis no tiene
# sesiones ORM (no hay commit/rollback) asi que no hay equivalente a
# session.py: el cliente que devuelve get_redis_client() ya es seguro para
# usar directo, redis-py administra su propio pool de conexiones interno.
#
#   settings.py  →  connection.py  →  redis_client.py (get_redis_client)

import redis

from ..settings import get_db_config
from .connection import build_connection_url

_redis_cache: dict = {}


def get_redis_client(prefix: str) -> redis.Redis:
    """Devuelve el cliente redis-py para el alias dado, creándolo si no existe en caché.

    El cliente es compartido por todo el proceso (singleton por alias), igual
    que get_engine() en engine.py. `prefix` es cualquier alias con sus
    variables de entorno definidas (ver settings.py), con DB_<ALIAS>_ENGINE=REDIS.
    """
    if prefix not in _redis_cache:
        config = get_db_config(prefix)
        url = build_connection_url(config)
        _redis_cache[prefix] = redis.Redis.from_url(url, decode_responses=True)
    return _redis_cache[prefix]