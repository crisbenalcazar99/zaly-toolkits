import logging
from unittest.mock import MagicMock

import pytest

from zaly_toolkits.ml.pipeline import LoggingPipeline


class DummyStep:
    """Transformer minimo: solo fit + transform (sin fit_transform propio)."""

    def __init__(self, output=None):
        self.output = output
        self.fit_args = None
        self.transform_args = None

    def fit(self, X, y=None):
        self.fit_args = (X, y)
        return self

    def transform(self, X):
        self.transform_args = X
        return self.output if self.output is not None else X


class DummyStepWithFitTransform(DummyStep):
    """Transformer con fit_transform propio, para probar la rama rapida."""

    def __init__(self, output=None):
        super().__init__(output)
        self.fit_transform_args = None

    def fit_transform(self, X, y=None):
        self.fit_transform_args = (X, y)
        return self.output if self.output is not None else X


@pytest.fixture
def fake_logger():
    return MagicMock()


class TestFitTransform:
    def test_encadena_los_steps_en_orden(self, fake_logger):
        step_1 = DummyStep(output="X1")
        step_2 = DummyStep(output="X2")
        pipeline = LoggingPipeline(steps=[("s1", step_1), ("s2", step_2)], logger=fake_logger)

        result = pipeline.fit_transform("X0", y="y0")

        assert step_1.fit_args == ("X0", "y0")
        assert step_1.transform_args == "X0"
        assert step_2.fit_args == ("X1", "y0")
        assert step_2.transform_args == "X1"
        assert result == "X2"

    def test_usa_fit_transform_propio_si_esta_disponible(self, fake_logger):
        step_1 = DummyStepWithFitTransform(output="X1")
        pipeline = LoggingPipeline(steps=[("s1", step_1)], logger=fake_logger)

        result = pipeline.fit_transform("X0", y="y0")

        assert step_1.fit_transform_args == ("X0", "y0")
        assert step_1.fit_args is None
        assert result == "X1"

    def test_usa_fallback_fit_luego_transform_si_no_hay_fit_transform(self, fake_logger):
        step_1 = DummyStep(output="X1")
        pipeline = LoggingPipeline(steps=[("s1", step_1)], logger=fake_logger)

        result = pipeline.fit_transform("X0", y="y0")

        assert step_1.fit_args == ("X0", "y0")
        assert step_1.transform_args == "X0"
        assert result == "X1"

    def test_loggea_inicio_y_fin_de_cada_step(self, fake_logger):
        step_1 = DummyStep()
        pipeline = LoggingPipeline(steps=[("s1", step_1)], pipeline_name="MiPipe", logger=fake_logger)

        pipeline.fit_transform("X0")

        mensajes = [call.args[0] for call in fake_logger.info.call_args_list]
        assert any("MiPipe" in m and "s1" in m and "started" in m for m in mensajes)
        assert any("MiPipe" in m and "s1" in m and "finished" in m for m in mensajes)


class TestTransform:
    def test_recorre_todos_los_steps_incluido_el_ultimo(self, fake_logger):
        step_1 = DummyStep(output="X1")
        step_2 = DummyStep(output="X2")
        pipeline = LoggingPipeline(steps=[("s1", step_1), ("s2", step_2)], logger=fake_logger)

        result = pipeline.transform("X0")

        assert step_1.transform_args == "X0"
        assert step_2.transform_args == "X1"
        assert result == "X2"

    def test_loggea_cada_step(self, fake_logger):
        step_1 = DummyStep()
        pipeline = LoggingPipeline(steps=[("s1", step_1)], pipeline_name="MiPipe", logger=fake_logger)

        pipeline.transform("X0")

        mensajes = [call.args[0] for call in fake_logger.info.call_args_list]
        assert any("MiPipe" in m and "Transform started" in m for m in mensajes)
        assert any("MiPipe" in m and "Transform finished" in m for m in mensajes)


class TestDefaults:
    def test_usa_logger_por_defecto_si_no_se_pasa_ninguno(self):
        pipeline = LoggingPipeline(steps=[("s1", DummyStep())])

        assert pipeline.logger is logging.getLogger("pipeline_logger")

    def test_pipeline_name_por_defecto(self):
        pipeline = LoggingPipeline(steps=[("s1", DummyStep())])

        assert pipeline.pipeline_name == "DefaultPipeline"