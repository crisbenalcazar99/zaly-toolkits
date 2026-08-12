from unittest.mock import MagicMock

import pytest

from zaly_toolkits.db import session as session_module


@pytest.fixture
def fake_session_maker(mocker):
    fake_session = MagicMock()
    mocker.patch.object(
        session_module, "get_session_maker", return_value=MagicMock(return_value=fake_session)
    )
    return fake_session


def test_get_session_hace_commit_y_close_si_no_hay_error(fake_session_maker):
    with session_module.get_session("QUANTA") as session:
        assert session is fake_session_maker

    fake_session_maker.commit.assert_called_once()
    fake_session_maker.rollback.assert_not_called()
    fake_session_maker.close.assert_called_once()


def test_get_session_hace_rollback_y_close_si_hay_error(fake_session_maker):
    with pytest.raises(ValueError):
        with session_module.get_session("QUANTA"):
            raise ValueError("boom")

    fake_session_maker.commit.assert_not_called()
    fake_session_maker.rollback.assert_called_once()
    fake_session_maker.close.assert_called_once()


def test_get_session_usa_local_como_alias_por_defecto(mocker):
    mock_get_session_maker = mocker.patch.object(
        session_module, "get_session_maker", return_value=MagicMock(return_value=MagicMock())
    )

    with session_module.get_session():
        pass

    mock_get_session_maker.assert_called_once_with("LOCAL")