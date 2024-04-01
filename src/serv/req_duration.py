# -*- coding: utf-8 -*-
import logging
import time

from starlette.requests import Request

from config.app_mdl import cfg

logger = logging.getLogger()


# Middleware
async def request_duration(request: Request, call_next):
    """Подсчитать и залогировать длительность выполнения запроса (если надо)"""
    if logging.root.getEffectiveLevel() >= cfg.timing_int:
        start_time = time.perf_counter()
        response = await call_next(request)  # передача запроса на дальнейшую обработку (конкретно - в эндпойнт)
        logger.debug(f"Request duration = {round(time.perf_counter() - start_time, 3)} sec")
    else:
        response = await call_next(request)

    return response
