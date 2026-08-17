from zaly_toolkits.db import redis_client as redis_client_module


def test_get_redis_client_crea_y_cachea(mocker, redis_config):
    mock_from_url = mocker.patch.object(redis_client_module.redis.Redis, "from_url")
    mocker.patch.object(redis_client_module, "get_db_config", return_value=redis_config)

    client_1 = redis_client_module.get_redis_client("QUANTA")
    client_2 = redis_client_module.get_redis_client("QUANTA")

    assert client_1 is client_2
    mock_from_url.assert_called_once()
    url, kwargs = mock_from_url.call_args.args[0], mock_from_url.call_args.kwargs
    assert url == "redis://app:secret@redishost:6379/2"
    assert kwargs == {"decode_responses": True}


def test_get_redis_client_prefijos_distintos_son_independientes(mocker, redis_config):
    mock_from_url = mocker.patch.object(redis_client_module.redis.Redis, "from_url")
    mocker.patch.object(redis_client_module, "get_db_config", return_value=redis_config)

    redis_client_module.get_redis_client("QUANTA")
    redis_client_module.get_redis_client("FENIX")

    assert mock_from_url.call_count == 2


def test_get_redis_client_socket_timeout_explicito_se_pasa_a_from_url(mocker, redis_config):
    mock_from_url = mocker.patch.object(redis_client_module.redis.Redis, "from_url")
    mocker.patch.object(redis_client_module, "get_db_config", return_value=redis_config)

    redis_client_module.get_redis_client(
        "QUANTA", socket_timeout=45, socket_connect_timeout=10
    )

    kwargs = mock_from_url.call_args.kwargs
    assert kwargs == {
        "decode_responses": True,
        "socket_timeout": 45,
        "socket_connect_timeout": 10,
    }


def test_get_redis_client_cachea_por_prefijo_y_timeouts(mocker, redis_config):
    mock_from_url = mocker.patch.object(
        redis_client_module.redis.Redis, "from_url", side_effect=lambda *a, **k: mocker.MagicMock()
    )
    mocker.patch.object(redis_client_module, "get_db_config", return_value=redis_config)

    client_default = redis_client_module.get_redis_client("QUANTA")
    client_timeout_45 = redis_client_module.get_redis_client("QUANTA", socket_timeout=45)
    client_timeout_45_again = redis_client_module.get_redis_client(
        "QUANTA", socket_timeout=45
    )

    assert client_default is not client_timeout_45
    assert client_timeout_45 is client_timeout_45_again
    assert mock_from_url.call_count == 2