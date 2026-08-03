# zaly_toolkits.db

Toolkit de conectividad a bases de datos. Da un estándar único para conectarse
a PostgreSQL y SQL Server vía SQLAlchemy, sin que cada proyecto tenga que
reimplementar construcción de URLs, manejo de engines o ciclo de vida de
sesiones.

## Uso

El único punto de entrada que el código de negocio debe importar es
`get_session`:

```python
from zaly_toolkits.db import get_session

with get_session("QUANTA") as session:
    session.execute(...)
```

`get_session` hace `commit` si el bloque termina sin errores, `rollback` si
hay una excepción, y siempre cierra la sesión al salir — el llamador no
gestiona el ciclo de vida.

`"QUANTA"` es un **alias**: un nombre lógico de base de datos, resuelto a su
configuración de conexión a través de variables de entorno (ver
[Configuración](#configuración)).

## Arquitectura

```
settings.py        connection.py           engine.py                  session.py
────────────       ─────────────           ─────────                  ──────────
get_db_config(  →   build_connection_url( →  get_engine(alias)     →  get_session(alias)
  alias)              config)                 get_session_maker(       (context manager:
                                               alias)                   commit/rollback/close)
lee env vars        arma el string de       crea y cachea el
por alias           conexión SQLAlchemy      engine/sessionmaker
                     según el motor           (singleton por alias)
```

- **`settings.py`** — lee la configuración de un alias desde variables de
  entorno (`pydantic-settings`) y la devuelve como dict.
- **`connection.py`** — único punto de construcción de la URL de conexión.
  Solo revisa el motor (`engine_database`) configurado y arma el string para
  PostgreSQL o SQL Server. No sabe nada de engines de SQLAlchemy ni de
  sesiones.
- **`engine.py`** — crea el `Engine` y el `sessionmaker` de SQLAlchemy a
  partir de la URL, y los cachea en memoria por alias (singleton por
  proceso: una sola pool de conexiones por BD, sin importar cuántas veces
  se pida).
- **`session.py`** — expone `get_session`, el context manager que usa el
  código de negocio. Es la única pieza de este paquete pensada para
  importarse fuera de `db/`.

No importar `connection.py` ni `engine.py` directamente desde código de
negocio; son detalles internos de implementación.

## Configuración

Cada alias se configura con variables de entorno con el prefijo
`DB_<ALIAS>_`:

| Variable                    | Obligatoria                          | Descripción                                    |
|------------------------------|---------------------------------------|-------------------------------------------------|
| `DB_<ALIAS>_ENGINE`           | Sí                                     | `POSTGRES` o `SQLSERVER`                        |
| `DB_<ALIAS>_HOST`             | Sí                                     | Host del servidor                               |
| `DB_<ALIAS>_PORT`             | Sí                                     | Puerto (entero)                                 |
| `DB_<ALIAS>_USER`             | Sí en POSTGRES / opcional en SQLSERVER | Usuario de la BD                                |
| `DB_<ALIAS>_PASSWORD`         | Sí en POSTGRES / opcional en SQLSERVER | Contraseña. En SQLSERVER, si se omite, se usa Trusted Connection (auth. de Windows) |
| `DB_<ALIAS>_ODBC_DRIVER`      | Sí en SQLSERVER                       | Nombre del driver ODBC, ej. `ODBC Driver 17 for SQL Server` |
| `DB_<ALIAS>_DB_NAME`          | No                                     | Base de datos por defecto. Si se omite, la conexión usa la BD por defecto del login/servidor |

Para agregar una BD nueva basta con definir sus variables de entorno; no hay
que tocar código. Para desarrollo local, las variables también se pueden
poner en un archivo `.env` en la raíz del proyecto (soporte vía
`pydantic-settings`).

### Ejemplo

```env
DB_QUANTA_ENGINE=POSTGRES
DB_QUANTA_HOST=localhost
DB_QUANTA_PORT=5432
DB_QUANTA_USER=app
DB_QUANTA_PASSWORD=secret
DB_QUANTA_DB_NAME=quanta

DB_FENIX_ENGINE=SQLSERVER
DB_FENIX_HOST=fenix-server
DB_FENIX_PORT=1433
DB_FENIX_ODBC_DRIVER=ODBC Driver 17 for SQL Server
# sin DB_FENIX_PASSWORD -> Trusted Connection
```

## Motores soportados

### PostgreSQL

```
postgresql+psycopg2://user:pass@host:port[/db_name]
```

### SQL Server

Con `password` (autenticación SQL):

```
mssql+pyodbc://user:pass@host:port[/db_name]?driver=...&TrustServerCertificate=yes
```

Sin `password` (Trusted Connection / autenticación de Windows — no se envía
`user` ni `password`):

```
mssql+pyodbc://@host:port[/db_name]?driver=...&TrustServerCertificate=yes&Trusted_Connection=yes
```

## Errores

Definidos en `zaly_toolkits/exceptions.py`:

- **`UnsupportedEngineError`** — `DB_<ALIAS>_ENGINE` no es `POSTGRES` ni
  `SQLSERVER`.
- **`MissingConfigError`** — falta algún campo obligatorio para el motor
  configurado (ver tabla de [Configuración](#configuración)).

## Dependencias

- `sqlalchemy`
- `pydantic-settings` (y `python-dotenv` para soporte de `.env`)
- Driver del motor que uses: `psycopg2`/`psycopg2-binary` para PostgreSQL,
  `pyodbc` para SQL Server (además del driver ODBC del sistema operativo).