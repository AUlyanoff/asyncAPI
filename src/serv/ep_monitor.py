#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from typing import Callable

from fastapi import Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute

logger = logging.getLogger(__name__)


class EPMonitor(APIRoute):
    """
    Наблюдает за стартом и завершением ендпойнта (endpoint monitor).
    Использование: добавлять этот класс в те роуты, за которыми хотим следить.
    Например, router = APIRouter(route_class=EPMonitor)
    """
    def get_route_handler(self) -> Callable:
        """Переопределение оригинального route_handler с интеграцией логирования"""
        original_route_handler = super().get_route_handler()    # сохраним текущий обработчик маршрута

        async def req2resp(req: Request) -> Response:
            """Принимает запрос, возвращает ответ"""

            # ------------------------------------------- вызов эндпойнта ---------------------------------------------
            try:
                resp: Response = await original_route_handler(req)

            # ------------------------------------------- обработка после эндпойнта -----------------------------------
            except RequestValidationError as e:
                logger.error(f"(After calling endpoint): {req.url}, error passing parameters to endpoint:\n\t{e}")
                raise e
            except Exception as e:   # todo накопить опыт, какие будут ошибки, и обработать их здесь
                logger.error(f'(After calling endpoint): {req.url}, unexpected error: {e}')
                raise e
            else:               # можно удалить ветку else после завершения накопления ошибок
                logger.debug(f'endpoint {req.url.path} ended without internal errors')

            return resp
            # ---------------------------------------------------------------------------------------------------------

        return req2resp

