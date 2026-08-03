# Punto de entrada público del toolkit de conectividad a BD.
# Ver db/README.md para la guía completa de uso y configuración.
from .session import get_session

__all__ = ["get_session"]