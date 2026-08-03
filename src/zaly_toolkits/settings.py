# settings.py — Lectura de configuración de conexión por alias de BD.
#
# Convención de variables de entorno para un alias ALIAS:
#   DB_<ALIAS>_ENGINE        POSTGRES | SQLSERVER
#   DB_<ALIAS>_HOST
#   DB_<ALIAS>_PORT
#   DB_<ALIAS>_USER          (opcional en SQLSERVER -> Trusted Connection)
#   DB_<ALIAS>_PASSWORD      (opcional en SQLSERVER -> Trusted Connection)
#   DB_<ALIAS>_ODBC_DRIVER   (solo SQLSERVER)
#   DB_<ALIAS>_DB_NAME       (opcional)
#
# Ej: get_db_config("QUANTA") lee DB_QUANTA_ENGINE, DB_QUANTA_HOST, etc.
# Para agregar una BD nueva basta con definir sus variables; no hay que
# tocar este archivo.
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class _DBAliasSettings(BaseSettings):
    """Config de conexión de un alias de BD, leída de variables de entorno.

    Los nombres de campo deben coincidir con el sufijo de la variable de
    entorno (DB_<ALIAS>_<CAMPO>): no usar `validation_alias` aquí, porque
    un alias explícito hace que pydantic-settings ignore el env_prefix y
    lea la variable "pelada" (ej. terminó leyendo el $USER del sistema
    operativo en vez de DB_<ALIAS>_USER).

    Los campos quedan Optional a propósito: la validación de "qué es
    obligatorio por motor" vive en connection.py::OBLIGATORIOS, no aquí.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    engine: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    user: Optional[str] = None
    password: Optional[str] = None
    odbc_driver: Optional[str] = None
    db_name: Optional[str] = None


def get_db_config(alias: str) -> dict:
    """Devuelve el dict de config de conexión para `alias`, leído del entorno.

    Este dict es el que espera connection.py::build_connection_url().
    """
    settings = _DBAliasSettings(_env_prefix=f"DB_{alias.upper()}_")
    config = settings.model_dump()
    config["engine_database"] = config.pop("engine")
    return config