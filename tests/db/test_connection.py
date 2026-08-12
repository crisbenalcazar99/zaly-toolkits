import pytest

from zaly_toolkits.db.connection import build_connection_url
from zaly_toolkits.exceptions import MissingConfigError, UnsupportedEngineError


class TestPostgres:
    def test_url_con_db_name(self, postgres_config):
        url = build_connection_url(postgres_config)
        assert url == "postgresql+psycopg2://app:secret@localhost:5432/app_db"

    def test_url_sin_db_name(self, postgres_config):
        postgres_config.pop("db_name")
        url = build_connection_url(postgres_config)
        assert url == "postgresql+psycopg2://app:secret@localhost:5432/"

    @pytest.mark.parametrize("campo", ["host", "port", "user", "password"])
    def test_falla_si_falta_campo_obligatorio(self, postgres_config, campo):
        postgres_config.pop(campo)
        with pytest.raises(MissingConfigError) as exc_info:
            build_connection_url(postgres_config)
        assert campo in exc_info.value.faltantes


class TestSqlServer:
    def test_url_con_password_usa_auth_sql(self, sqlserver_config):
        url = build_connection_url(sqlserver_config)
        assert url == (
            "mssql+pyodbc://app:secret@sqlhost:1433/app_db"
            "?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
        )

    def test_url_sin_password_usa_trusted_connection(self, sqlserver_config):
        sqlserver_config.pop("password")
        sqlserver_config.pop("user")
        url = build_connection_url(sqlserver_config)
        assert url == (
            "mssql+pyodbc://@sqlhost:1433/app_db"
            "?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
            "&Trusted_Connection=yes"
        )

    def test_url_sin_db_name(self, sqlserver_config):
        sqlserver_config.pop("db_name")
        url = build_connection_url(sqlserver_config)
        assert url.startswith("mssql+pyodbc://app:secret@sqlhost:1433/?driver=")

    def test_falla_si_hay_password_pero_no_user(self, sqlserver_config):
        sqlserver_config.pop("user")
        with pytest.raises(MissingConfigError) as exc_info:
            build_connection_url(sqlserver_config)
        assert exc_info.value.faltantes == ["user"]

    @pytest.mark.parametrize("campo", ["host", "port", "odbc_driver"])
    def test_falla_si_falta_campo_obligatorio(self, sqlserver_config, campo):
        sqlserver_config.pop(campo)
        with pytest.raises(MissingConfigError) as exc_info:
            build_connection_url(sqlserver_config)
        assert campo in exc_info.value.faltantes


class TestRedis:
    def test_url_con_password_incluye_credenciales(self, redis_config):
        url = build_connection_url(redis_config)
        assert url == "redis://app:secret@redishost:6379/2"

    def test_url_sin_password_no_incluye_credenciales(self, redis_config):
        redis_config.pop("password")
        redis_config.pop("user")
        url = build_connection_url(redis_config)
        assert url == "redis://redishost:6379/2"

    def test_url_sin_db_index_usa_0_por_defecto(self, redis_config):
        redis_config.pop("db_index")
        url = build_connection_url(redis_config)
        assert url == "redis://app:secret@redishost:6379/0"

    @pytest.mark.parametrize("campo", ["host", "port"])
    def test_falla_si_falta_campo_obligatorio(self, redis_config, campo):
        redis_config.pop(campo)
        with pytest.raises(MissingConfigError) as exc_info:
            build_connection_url(redis_config)
        assert campo in exc_info.value.faltantes


class TestMotorNoSoportado:
    def test_motor_desconocido(self, postgres_config):
        postgres_config["engine_database"] = "ORACLE"
        with pytest.raises(UnsupportedEngineError) as exc_info:
            build_connection_url(postgres_config)
        assert exc_info.value.engine == "ORACLE"

    def test_motor_ausente(self, postgres_config):
        postgres_config.pop("engine_database")
        with pytest.raises(UnsupportedEngineError):
            build_connection_url(postgres_config)