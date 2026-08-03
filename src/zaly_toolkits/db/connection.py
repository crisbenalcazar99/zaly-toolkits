# connection.py — Construcción de URLs de conexión para SQLAlchemy.
#
# Soporta PostgreSQL (psycopg2) y SQL Server (pyodbc via ODBC).
# Es llamado exclusivamente por engine.py::get_engine(); no debe usarse directo
# desde código de negocio (usar db/session.py::get_session()).
from ..exceptions import UnsupportedEngineError, MissingConfigError


OBLIGATORIOS = {
    "POSTGRES": {"host", "port", "user", "password"},
    # user/password son opcionales en SQLSERVER: si no se envía "password"
    # se arma la cadena con Trusted_Connection (autenticación de Windows).
    # db_name es opcional en ambos motores: si no se envía, se conecta a la
    # base de datos por defecto del login/servidor.
    "SQLSERVER": {"host", "port", "odbc_driver"},
}

DEFAULT_CONFIG_ENGINE = {
    "POSTGRES": {"engine": "postgresql", "driver": "psycopg2"},
    "SQLSERVER": {"engine": "mssql", "driver": "pyodbc"},
}
ENGINES_SOPORTADOS = DEFAULT_CONFIG_ENGINE.keys()

def build_connection_url(config: dict) -> str:
    """Punto único de construcción del string de conexión SQLAlchemy.

    Solo revisa el motor configurado (`engine_database`) y delega la
    construcción de la cadena al builder correspondiente.

    Para PostgreSQL produce:
        postgresql+psycopg2://user:pass@host:port[/db_name]

    Para SQL Server, si se envía "password" produce autenticación SQL:
        mssql+pyodbc://user:pass@host:port[/db_name]?driver=...&TrustServerCertificate=yes

    Para SQL Server, si NO se envía "password" produce Trusted Connection (auth. de Windows):
        mssql+pyodbc://@host:port[/db_name]?driver=...&TrustServerCertificate=yes&Trusted_Connection=yes

    `db_name` es opcional en ambos motores: si no viene en `config`, la URL
    se arma sin ese segmento y la conexión usa la base de datos por defecto
    del login/servidor.

    El dict `config` es el que devuelve settings.py::get_db_config().
    """
    engine_database = config.get("engine_database")

    if engine_database not in ENGINES_SOPORTADOS:
        raise UnsupportedEngineError(engine_database, ENGINES_SOPORTADOS)

    faltantes = [c for c in OBLIGATORIOS[engine_database] if not config.get(c)]
    if faltantes:
        raise MissingConfigError(faltantes, engine_database)

    if engine_database == "POSTGRES":
        return _build_postgres_url(config)
    if engine_database == "SQLSERVER":
        return _build_sqlserver_url(config)
    return None


def _build_postgres_url(config: dict) -> str:
    """Arma la URL de PostgreSQL. Asume que OBLIGATORIOS ya fue validado."""
    engine = DEFAULT_CONFIG_ENGINE["POSTGRES"]
    user = config["user"]
    password = config["password"]
    host = config["host"]
    port = config["port"]
    db_name = config.get("db_name", "")

    return f"{engine['engine']}+{engine['driver']}://{user}:{password}@{host}:{port}/{db_name}"


def _build_sqlserver_url(config: dict) -> str:
    """Arma la URL de SQL Server; decide auth SQL vs. Trusted Connection según `password`."""
    engine = DEFAULT_CONFIG_ENGINE["SQLSERVER"]
    host = config["host"]
    port = config["port"]
    db_name = config.get("db_name", "")
    odbc_driver_encoded = config["odbc_driver"].replace(" ", "+")
    password = config.get("password")

    if password:
        user = config.get("user")
        if not user:
            raise MissingConfigError(["user"], "SQLSERVER")
        credenciales = f"{user}:{password}@"
        auth_query = ""
    else:
        # Sin contraseña -> Trusted Connection (autenticación de Windows),
        # no se envía user ni password.
        credenciales = "@"
        auth_query = "&Trusted_Connection=yes"

    return (
        f"{engine['engine']}+{engine['driver']}://{credenciales}{host}:{port}/{db_name}"
        f"?driver={odbc_driver_encoded}&TrustServerCertificate=yes{auth_query}"
    )