import logging
import pytest
from fastapi.testclient import TestClient
from app.app_init import app
from httpx import AsyncClient
import json

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_user_list_ok():
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.post('/api/v1/users/list',
                       json=[
                           {
                               "uid": "ru.niisokb.safestore",
                               "title": "SafeStore",
                               "versionName": "1.1.5",
                               "versionCode": "1001005",
                               "enabled": True
                           }
                       ]
                       )
        assert resp.status_code == 200


# @pytest.mark.asyncio
def test_async_logging():
    """Асинхронный тест для проверки уникальности номера запроса в контексте разных экземпляров корутины"""

    # async with AsyncClient(app=app, base_url="http://test") as ac:
    # ac = AsyncClient(app=app, base_url="http://test")
    with TestClient(app=app, base_url="http://test") as client:
        bodies = [{"uid": "ru.test.01", "title": "Safe01", "versionName": "1.1", "versionCode": 10, "enabled": True},
                  {"uid": "ru.test.02", "title": "Safe02", "versionName": "1.2", "versionCode": 20, "enabled": True},
                  {"uid": "ru.test.03", "title": "Safe03", "versionName": "1.3", "versionCode": 30, "enabled": True},
                  {"uid": "ru.test.04", "title": "Safe04", "versionName": "1.4", "versionCode": 40, "enabled": True},
                  {"uid": "ru.test.05", "title": "Safe05", "versionName": "1.5", "versionCode": 50, "enabled": True},
                  ]

        for body in bodies:
            body = json.dumps([body], ensure_ascii=False)
            resp = client.post(url=f"api/v1/users/list", content=body)
            assert resp.status_code == 200
