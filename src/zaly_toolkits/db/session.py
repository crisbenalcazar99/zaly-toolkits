# session.py — Context manager de sesiones para código de negocio.
#
# Es la opción recomendada para el caso común: garantiza commit, rollback y
# cierre automático sin que el llamador tenga que gestionar el ciclo de vida.
# Para casos que necesiten control manual (ej. una transacción que abarca
# varias funciones), usar engine.py::get_session_maker() o get_engine()
# directo — ambos son parte de la API pública del toolkit (ver db/__init__.py).
#
# Para agregar una nueva BD basta con definir sus variables de entorno
# (DB_<ALIAS>_HOST, DB_<ALIAS>_PORT, etc. — ver settings.py) — no hay que
# modificar este archivo.
#
# Uso:
#   with get_session("QUANTA") as session:
#       session.execute(...)

from contextlib import contextmanager
from .engine import get_session_maker


@contextmanager
def get_session(db_alias: str = "LOCAL"):
    """Context manager que entrega una sesión SQLAlchemy lista para usar.

    Hace commit al salir sin error, rollback si hay excepción, y siempre cierra.
    db_alias es el prefijo de la BD: LOCAL, PORTAL, PORTAL_GK, FENIX,
    CAMUNDA, LATINUM, QUANTA, o cualquier prefijo nuevo definido en .env.
    """
    session = get_session_maker(db_alias)()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
