# engine.py — Crea y cachea los engines/sessionmakers de SQLAlchemy.
#
# Mantiene un cache por alias (singleton por proceso) para no crear
# múltiples engines/pools de conexión para la misma BD. El flujo completo es:
#
#   settings.py  →  connection.py  →  engine.py (get_engine/get_session_maker)
#
# Desde código de negocio NO se debe importar este módulo directamente;
# usar session.py::get_session() que agrega el context manager (commit/rollback/close).

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..settings import get_db_config
from .connection import build_connection_url

# Punto de extensión: kwargs extra de create_engine por prefijo
# (ej. {"QUANTA": {"pool_size": 10}}), para casos que no se resuelven
# vía la URL de conexión.
_CONNECT_ARGS: dict = {}

_engine_cache: dict = {}
_session_cache: dict = {}


def get_engine(prefix: str):
    """Devuelve el engine SQLAlchemy para el alias dado, creándolo si no existe en caché.

    El engine es compartido por todo el proceso (singleton por alias): la
    primera llamada para un alias crea el engine (y su pool de conexiones);
    las siguientes reutilizan la misma instancia. `prefix` puede ser
    cualquier alias con sus variables de entorno definidas (ver settings.py).
    """
    if prefix not in _engine_cache:
        config = get_db_config(prefix)
        url = build_connection_url(config)
        extra = _CONNECT_ARGS.get(prefix, {})
        _engine_cache[prefix] = create_engine(url, echo=False, hide_parameters=True, **extra)
    return _engine_cache[prefix]


def get_session_maker(prefix: str):
    """Devuelve el sessionmaker (singleton por alias) para el prefijo dado.

    Úsalo cuando necesites instanciar sesiones manualmente.
    Para la mayoría de los casos prefiere session.py::get_session().
    """
    if prefix not in _session_cache:
        _session_cache[prefix] = sessionmaker(
            autocommit=False, autoflush=False, bind=get_engine(prefix)
        )
    return _session_cache[prefix]


