from unittest.mock import MagicMock

from zaly_toolkits.db import engine as engine_module


def test_get_engine_crea_y_cachea(mocker, postgres_config):
    mock_create_engine = mocker.patch.object(engine_module, "create_engine")
    mocker.patch.object(engine_module, "get_db_config", return_value=postgres_config)

    engine_1 = engine_module.get_engine("QUANTA")
    engine_2 = engine_module.get_engine("QUANTA")

    assert engine_1 is engine_2
    mock_create_engine.assert_called_once()
    url, kwargs = mock_create_engine.call_args.args[0], mock_create_engine.call_args.kwargs
    assert url == "postgresql+psycopg2://app:secret@localhost:5432/app_db"
    assert kwargs == {"echo": False, "hide_parameters": True}


def test_get_engine_prefijos_distintos_son_independientes(mocker, postgres_config):
    mock_create_engine = mocker.patch.object(engine_module, "create_engine")
    mocker.patch.object(engine_module, "get_db_config", return_value=postgres_config)

    engine_module.get_engine("QUANTA")
    engine_module.get_engine("FENIX")

    assert mock_create_engine.call_count == 2


def test_get_engine_usa_connect_args_extra_por_prefijo(mocker, postgres_config):
    mock_create_engine = mocker.patch.object(engine_module, "create_engine")
    mocker.patch.object(engine_module, "get_db_config", return_value=postgres_config)
    mocker.patch.object(engine_module, "_CONNECT_ARGS", {"QUANTA": {"pool_size": 10}})

    engine_module.get_engine("QUANTA")

    assert mock_create_engine.call_args.kwargs["pool_size"] == 10


def test_get_session_maker_se_liga_al_engine_y_se_cachea(mocker, postgres_config):
    mocker.patch.object(engine_module, "get_db_config", return_value=postgres_config)
    fake_engine = MagicMock()
    mocker.patch.object(engine_module, "create_engine", return_value=fake_engine)

    session_maker = engine_module.get_session_maker("QUANTA")
    session = session_maker()

    assert session.bind is fake_engine
    assert engine_module.get_session_maker("QUANTA") is session_maker