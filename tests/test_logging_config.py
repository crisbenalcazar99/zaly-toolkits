import logging

import pytest

from zaly_toolkits.logging_config import setup_logger


@pytest.fixture
def _snapshot_root_logger():
    """setup_logger usa force=True y resetea el root logger; hay que restaurarlo
    despues de cada test para no filtrar config entre tests."""
    root = logging.getLogger()
    original_handlers = root.handlers[:]
    original_level = root.level
    yield
    root.handlers[:] = original_handlers
    root.level = original_level


def test_no_escribe_archivo_si_log_file_es_none(_snapshot_root_logger):
    setup_logger(log_file=None)

    handlers = logging.getLogger().handlers
    assert len(handlers) == 1
    assert isinstance(handlers[0], logging.StreamHandler)
    assert not any(isinstance(h, logging.FileHandler) for h in handlers)


def test_agrega_file_handler_si_se_especifica_log_file(_snapshot_root_logger, tmp_path):
    log_file = tmp_path / "test.log"

    setup_logger(log_file=log_file)

    file_handlers = [h for h in logging.getLogger().handlers if isinstance(h, logging.FileHandler)]
    assert len(file_handlers) == 1
    assert file_handlers[0].baseFilename == str(log_file)


def test_respeta_el_nivel_configurado(_snapshot_root_logger):
    setup_logger(level=logging.DEBUG, log_file=None)

    assert logging.getLogger().level == logging.DEBUG


def test_silencia_loggers_verbosos_de_sqlalchemy(_snapshot_root_logger):
    setup_logger(log_file=None)

    for name in (
        "sqlalchemy.engine",
        "sqlalchemy.engine.Engine",
        "sqlalchemy.pool",
        "sqlalchemy.dialects",
    ):
        assert logging.getLogger(name).level == logging.WARNING


def test_agrega_handlers_extra(_snapshot_root_logger):
    extra_handler = logging.NullHandler()

    setup_logger(log_file=None, extra_handlers=[extra_handler])

    assert extra_handler in logging.getLogger().handlers