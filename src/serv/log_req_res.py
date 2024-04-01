# -*- coding: utf-8 -*-
import logging
import re

from starlette.requests import Request
from starlette.concurrency import iterate_in_threadpool

from serv.log_utils import format_flatten_dict, trunc_str

logger = logging.getLogger()


# Middleware
async def log_req_res(req: Request, call_next):
    """Логирование запросов/ответов, КОТОРЫЕ НЕ ОБРАБАТЫВАЕТ FastAPI
       например 404, 405 обрабатывает httpx
       Функция зарегистрирована при загрузке сервера как middleware.
    """
    # ----------------------------------------------- логирование запроса ---------------------------------------------
    if logger.getEffectiveLevel() <= logging.INFO:  # только для INFO и DEBUG
        ll = f"\n\n\t≡>\t\t{req.method} {req.url} processing request started..."
        ll += f"\n\thead\t{format_flatten_dict(dict(req.headers))}"

        body = await req.body()
        if body:
            body = body.decode() if hasattr(body, 'decode') else body
            body = re.sub(r"\s+", " ", body)
            ll += f"\n\tbody \t{trunc_str(body)}"

        logger.info(ll)

    # ------------------------------------------ вызов эндпойнта ------------------------------------------------------
    resp = await call_next(req)

    # ------------------------------------------логирование ответа ----------------------------------------------------
    resp.headers['X-Frame-Options'] = 'DENY'  # запрет на отображение во фреймах [#22896]

    ll = f"\n\t<≡\t\t{req.method} {req.url.path} processing request HTTP={resp.status_code} " \
         f"{'ended' if 200 <= resp.status_code <= 299 else 'failed'}"
    ll += "\n\thead\t" + format_flatten_dict(dict(resp.headers))  # заголовки ответа

    if hasattr(resp, 'body'):   # есть body, который сделал эндпойнт
        ll += "\n\tbody\t" + trunc_str(getattr(resp, 'body', b'None').decode())  # тело ответа
    else:                       # body тоже есть, но его сделал не эндпойнт и не FastAPI, это body-итератор
        resp_body = [part async for part in resp.body_iterator]         # собираем боди по кусочкам в список
        ll += "\n\tbody\t" + trunc_str(b''.join(resp_body).decode())    # и логируем тело ответа как строку
        resp.body_iterator = iterate_in_threadpool(iter(resp_body))     # восстанавливаем body-итератор как было

    # ошибку логируем обязательно, а успех в зависимости от установленного уровня логирования
    if 200 <= resp.status_code <= 299 or resp.status_code == 302 or resp.status_code == 475:
        logger.info(ll)
    else:
        logger.error(ll)

    return resp
