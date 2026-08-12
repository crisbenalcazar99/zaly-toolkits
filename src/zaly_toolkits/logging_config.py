# logging_config.py — Configuracion centralizada de logging para toda la app.
#
# `log_file` y `extra_handlers` son parametrizables (en vez de estar hardcodeados)
# para que setup_logger() se pueda testear sin escribir a disco ni pisar la
# config global de logging entre tests: pasa log_file=None para desactivar el
# FileHandler.
import logging
from pathlib import Path
from typing import Optional, Union

_SQLALCHEMY_LOGGERS = (
    "sqlalchemy.engine",
    "sqlalchemy.engine.Engine",
    "sqlalchemy.pool",
    "sqlalchemy.dialects",
)


def setup_logger(
    level: int = logging.INFO,
    log_file: Optional[Union[str, Path]] = "errores_sqlalchemy.log",
    extra_handlers: Optional[list[logging.Handler]] = None,
) -> None:
    """Configura el root logger de la app (formato, nivel, handlers).

    `force=True` resetea cualquier configuracion previa de logging.basicConfig.
    Silencia por separado el logging verboso de SQLAlchemy a WARNING.
    """
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file is not None:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    if extra_handlers:
        handlers.extend(extra_handlers)

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
        force=True,
    )

    for name in _SQLALCHEMY_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)