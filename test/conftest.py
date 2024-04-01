# # -*- coding: utf-8 -*-
import logging
# from typing import NamedTuple
# from unittest.mock import MagicMock, AsyncMock
#
import pytest
# from starlette.testclient import TestClient
#
# import database
#
logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def probe():
    logger.debug('--- <<< ((( я фикстура ))) >>> ---')

#
#
# class DefaultOut(NamedTuple):
#     o_rc: int
#     o_err: str
#
#
# @pytest.fixture(autouse=True, scope='function')
# def mock_db():
#     # mock получения пула и получения конекта из пула, делается один раз на все тесты
#     if not isinstance(database.db.get_connection_from_pool, MagicMock):
#         database.db.make_connection_pool = AsyncMock()
#         database.db.get_connection_from_pool = MagicMock(database.db.get_connection_from_pool)
#
#     # mock всех процедур перед каждым тестом, чтобы не было неожиданного поведения, если забыл заполнить .return_value
#     for procedure in dir(database.db):
#         if procedure.startswith('sp_'):
#             setattr(database.db, procedure, AsyncMock())
#
#     # mock проверки версии
#     database.db.sp_components_imdm_version_check.return_value = DefaultOut(0, ''),


# @pytest.fixture(autouse=True)
# def client(request):
#     """Финализатор вызова API"""
#     from app.app_init import app
#
#     with TestClient(app) as client:
#         yield client
#         # этот код будет выполнен после завершения ендпойнта
