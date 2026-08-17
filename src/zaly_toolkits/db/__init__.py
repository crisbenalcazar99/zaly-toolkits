# Punto de entrada público del toolkit de conectividad a BD.
# Ver db/README.md para la guía completa de uso y configuración.
#
# Tres niveles disponibles segun cuanto control necesites:
#   get_session(alias)       -> sesion gestionada (commit/rollback/close automatico)
#   get_session_maker(alias) -> sesion manual, vos controlas el ciclo de vida
#   get_engine(alias)        -> conexion cruda (get_engine(alias).connect()), sin ORM
from .session import get_session
from .engine import get_engine, get_session_maker
from .redis_client import get_redis_client

__all__ = ["get_session", "get_session_maker", "get_engine", "get_redis_client"]