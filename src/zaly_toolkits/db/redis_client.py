# redis_client.py — Crea y cachea clientes redis-py por alias.
#
# Mismo patron de singleton por alias que engine.py, pero Redis no tiene
# sesiones ORM (no hay commit/rollback) asi que no hay equivalente a
# session.py: el cliente que devuelve get_redis_client() ya es seguro para
# usar directo, redis-py administra su propio pool de conexiones interno.
#
#   settings.py  →  connection.py  →  redis_client.py (get_redis_client)

from typing import Optional

import redis

from ..settings import get_db_config
from .connection import build_connection_url

_redis_cache: dict = {}


def get_redis_client(
    prefix: str,
    *,
    socket_timeout: Optional[float] = None,
    socket_connect_timeout: Optional[float] = None,
) -> redis.Redis:
    """Devuelve el cliente redis-py para el alias dado, creándolo si no existe en caché.

    El cliente es compartido por todo el proceso (singleton por alias + timeouts
    pedidos), igual que get_engine() en engine.py. `prefix` es cualquier alias
    con sus variables de entorno definidas (ver settings.py), con
    DB_<ALIAS>_ENGINE=REDIS.

    redis-py 8.x aplica un socket_timeout/socket_connect_timeout por defecto de
    5s si no se especifica ninguno (antes era None/bloqueante). Ese límite vive
    en el socket, no en el comando: corta la lectura a los 5s aunque le pases
    un timeout mayor a un comando bloqueante (BLPOP, BRPOP, etc.). Si tu caso
    de uso necesita esperar más, pasa socket_timeout explícito.
    """
    cache_key = (prefix, socket_timeout, socket_connect_timeout)
    if cache_key not in _redis_cache:
        config = get_db_config(prefix)
        url = build_connection_url(config)
        kwargs = {"decode_responses": True}
        if socket_timeout is not None:
            kwargs["socket_timeout"] = socket_timeout
        if socket_connect_timeout is not None:
            kwargs["socket_connect_timeout"] = socket_connect_timeout
        _redis_cache[cache_key] = redis.Redis.from_url(url, **kwargs)
    return _redis_cache[cache_key]