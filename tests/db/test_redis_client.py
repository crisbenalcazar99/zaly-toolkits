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