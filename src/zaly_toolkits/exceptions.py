"""  EXCEPCIONES PROPIAS DEL PAQUETE """

class ZalyToolkitsError(Exception):
    """Base de todas las excepciones de la librería."""

class ConfigError(ZalyToolkitsError):
    """Configuración inválida, incompleta o mal formada."""

class UnsupportedEngineError(ConfigError):
    """El motor de base de datos solicitado no está soportado."""
    def __init__(self, engine, soportados):
        self.engine = engine
        self.soportados = soportados
        super().__init__(
            f"Motor '{engine}' no soportado. "
            f"Disponibles: {', '.join(self.soportados)}"
        )

class MissingConfigError(ConfigError):
    """Faltan uno o más parámetros obligatorios de configuración."""
    def __init__(self, faltantes, engine=None):
        self.faltantes = sorted(faltantes)
        self.engine = engine
        contexto = f"para '{engine}'" if engine else ""
        super().__init__(
            f"Faltan parámetros obligatorios{contexto}: "
            f"{', '.join(self.faltantes)}"
        )