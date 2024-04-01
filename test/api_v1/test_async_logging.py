# -*- coding: utf-8 -*-
import pytest
from httpx import AsyncClient
import json

from app.app_init import app


# @pytest.mark.asyncio
async def test_async_logging():
    """Асинхронный тест для проверки уникальности номера запроса в контексте разных экземпляров корутины"""

    async with AsyncClient(app=app, base_url="http://test") as ac:
        bodies = [{"uid": "ru.test.01", "title": "Safe01", "versionName": "1.1", "versionCode": 10, "enabled": True},
                  {"uid": "ru.test.02", "title": "Safe02", "versionName": "1.2", "versionCode": 20, "enabled": True},
                  {"uid": "ru.test.03", "title": "Safe03", "versionName": "1.3", "versionCode": 30, "enabled": True},
                  {"uid": "ru.test.04", "title": "Safe04", "versionName": "1.4", "versionCode": 40, "enabled": True},
                  {"uid": "ru.test.05", "title": "Safe05", "versionName": "1.5", "versionCode": 50, "enabled": True},
                  ]

        for body in bodies:
            body = json.dumps([body], ensure_ascii=False)
            resp = await ac.post(url=f"api/v1/users/list", content=body)
            assert resp.status_code == 200
