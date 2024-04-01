# -*- coding: utf-8 -*-
import logging

from fastapi import Request
from fastapi.responses import PlainTextResponse
from fastapi.exceptions import RequestValidationError
from asyncpg.exceptions._base import PostgresError
from sqlalchemy.exc import ProgrammingError, InterfaceError, DBAPIError
from asyncpg import InternalServerError
# from database.exceptions import DatabaseException, ResultCheckException
from fastapi import HTTPException
from fastapi.exception_handlers import http_exception_handler
# from serv.consts import db_errs


from config.db_mdl import db_cfg
from serv.log_utils import format_flatten_dict, trunc_str
from sqlalchemy.exc import DBAPIError

logger = logging.getLogger(__name__)

# sqlalchemy.exc.DBAPIError: (sqlalchemy.dialects.postgresql.asyncpg.Error) \
# <class 'asyncpg.exceptions.ConnectionDoesNotExistError'>: connection was closed in the middle of operation


async def all_err(req: Request, e: Exception):
    """Универсальный обработчик исключений"""
    """ВНИМАНИЕ 
       Если FastAPI.debug == True, то перехват Exception подавляется и управление из FastAPI сюда не попадает
    """
    ll = f'\n\t<~\t\t{all_err.__doc__} ({getattr(type(e), "__name__", "Exception")}): ' \
         f'{req.url.path}, {req.scope["endpoint"].__name__}'

    content, stat = 'Unexpected server error', 575
    if isinstance(e, HTTPException):
        print(e)
    elif isinstance(e, DBAPIError):
        response = PlainTextResponse(content=content, status_code=stat)
        ll += f'\n\t\t\tUnsuccessful attempt database reading. '
        if hasattr(e, 'code') and hasattr(e, 'orig'):
            ll += f'{getattr(type(e), "__name__", "Error")} {e.code}, {e.orig.args[0].split(">: ")[-1]}'
        ll += f"\n\t<≡\t\t{req.method} {req.url.path} processing req HTTP={stat} ended"
        ll += "\n\thead\t" + format_flatten_dict(dict(response.headers))  # заголовки ответа
        ll += "\n\tdata\t" + trunc_str(response.body.decode())  # тело ответа
        ll += "\n\terror\t" + trunc_str(e)  # оригинал ошибки
    else:                                                   # наша обработка не предусмотрена
        ll += f'\n\t<~\t\t{all_err.__doc__} handler ({getattr(type(e), "__name__", "Exception")}): ' \
              f'there is no special handling for this exception, return to system...'
        logger.debug(ll)

        if isinstance(e, HTTPException):
            return await http_exception_handler(req, e)     # вернём в FastAPI, пусть обрабатывает как его учили
        else:
            raise                                           # вернём исключение интерпретатору, мы с FastAPI не умеем

    logger.error(ll)
    response = PlainTextResponse(content=content, status_code=stat)
    return response


async def interface_err(req: Request, e: InterfaceError):
    """Коннект с базой оборвался ?"""
    ll = f'\n\t<~\t\t{getattr(type(e), "__name__", "Error")} handler: {req.url.path}, {req.scope["endpoint"].__name__}'
    stat = 575
    response = PlainTextResponse(content='Unexpected server error', status_code=stat)

    ll += f'\n\t\t\tUnsuccessful attempt database reading. '
    if hasattr(e, 'code') and hasattr(e, 'orig'):
        ll += f'{getattr(type(e), "__name__", "Error")} {e.code}, {e.orig.args[0].split(">: ")[-1]}'
    ll += f"\n\t<≡\t\t{req.method} {req.url.path} processing req HTTP={stat} ended"
    ll += "\n\thead\t" + format_flatten_dict(dict(response.headers))  # заголовки ответа
    ll += "\n\tdata\t" + trunc_str(response.body.decode())  # тело ответа
    ll += "\n\terror\t" + trunc_str(e)  # оригинал ошибки

    logger.error(ll)
    return response


async def authentication(req: Request, e: InternalServerError):
    """То ли юзер, то ли пароль, то ли хост, то ли название базы"""
    ll = f'\n\t<~\t\t{getattr(type(e), "__name__", "Error")} handler: {req.url.path}, {req.scope["endpoint"].__name__}'
    stat = 575
    response = PlainTextResponse(content='Unexpected server error', status_code=stat)

    if getattr(e, 'sqlstate', '') == 'XX000':
        if 'password authentication failed' in getattr(e, "message", ""):
            ll += ('Check host, user or password...')
            # sys.tracebacklimit = 0  # страусов не пугать, пол бетонный
        elif 'database ' + db_cfg.name + ' does not exist' in getattr(e, "message", "").replace('"', ''):
            ll += ('Check DB name...')
            # sys.tracebacklimit = 0

    ll += f'\n\t\t\tUnsuccessful attempt database reading.' \
          f'\n\t\t\t, sqlalchemy InternalServerError code = f405, sqlstate = XX000'

    ll += f"\n\t<≡\t\t{req.method} {req.url.path} processing request HTTP={stat} ended"
    ll += "\n\thead\t" + format_flatten_dict(dict(response.headers))  # заголовки ответа
    ll += "\n\tdata\t" + trunc_str(response.body.decode())  # тело ответа
    ll += "\n\terror\t" + trunc_str(e)  # оригинал ошибки

    logger.error(ll)
    return response


async def tabel_not_found(req: Request, e: ProgrammingError):
    """Такой таблицы в базе нет"""
    ll = f'\n\t<~\t\t{getattr(type(e), "__name__", "Error")} handler: {req.url.path}, {req.scope["endpoint"].__name__}'
    stat = 575
    response = PlainTextResponse(content='Unexpected server error', status_code=stat)

    if getattr(e, 'code', None) == 'f405':
        if getattr(e, 'orig', None):
            if getattr(e.orig, 'sqlstate') == '42P01':
                if len(e.orig.args) > 0:
                    err_msg = e.orig.args[0].split(': ')[-1]
                    ll += f'\n\t\t\tUnsuccessful attempt database reading.' \
                          f'\n\t\t\t{err_msg}, sqlalchemy ProgrammingError code = f405, sqlstate = 42P01'
    ll += f"\n\t<≡\t\t{req.method} {req.url.path} processing request HTTP={stat} ended"
    ll += f"\n\thead\t{format_flatten_dict(dict(response.headers))}"  # заголовки ответа
    ll += f"\n\tdata\t{trunc_str(response.body.decode())}"  # тело ответа
    ll += f"\n\terror\t{trunc_str(e)}"  # оригинал ошибки

    logger.error(ll)
    return response


async def pydantic(req: Request, e: RequestValidationError):
    """Обработчик исключений от Pydantic"""
    """FastApi вызывает Pydantic
       - съедает исключение Pydantic-а ValidationError,
       - добавляет свои обработки и
       - перевозбуждает исключение под именем RequestValidationError
    """
    ll = f'\n\t<~\t\tPydantic validation error: {req.url.path}, {req.scope["endpoint"].__name__}'

    ls = list()
    if 'pydantic' in str(e.errors()).lower():
        stat = 400
        response = PlainTextResponse(content='Bad request. Wrong body', status_code=stat)
        for error in e.errors():
            ls.append(f"\t\t\t- {str(error.get('type'))[:16]:<16} "
                      f"{(': ').join(error.get('loc')):<20} = {str(error.get('input')):<12} {error.get('msg')}.")
    elif 'json_invalid' in str(e.errors()).lower():
        stat = 400
        response = PlainTextResponse(content='Bad request. Invalid json', status_code=stat)
    else:
        # todo накопить опыт и обработать другие случаи здесь, а пока http=500
        stat = 500
        response = PlainTextResponse(content='Unexpected RequestValidationError', status_code=stat)

    ll += '\n'.join(ls)
    ll += f"\n\t<≡\t\t{req.method} {req.url.path} processing request HTTP={stat} ended"
    ll += f"\n\thead\t{format_flatten_dict(dict(response.headers))}"  # заголовки ответа
    ll += f"\n\tdata\t{trunc_str(response.body.decode())}"  # тело ответа

    logger.error(ll)

    return response


# async def database_exception_handler(req: Request, e: DatabaseException):
#     """Обработчик исключения базы данных - заготовка для обрывов коннектов во время счёта"""
#     response = PlainTextResponse(content='DatabaseError', status_code=500)
#     ll = f"\n\t<≡\t\t{req.method} {req.url.path} processing request ended, HTTP={response.status_code}"
#     ll += "\n\thead\t" + format_flatten_dict(dict(response.headers))
#     ll += "\n\tdata\t" + trunc_str(response.body.decode())
#     sqlstate = getattr(e.exception, 'sqlstate', None)
#     detail = getattr(e.exception, 'detail', None)
#
#     ll += f"\n\t\t\tError executing SP {e.proc_name}" \
#           f"\n\t\t\t{db_errs.get(sqlstate, 'Unexpected database error')} " \
#           f"asyncpg: {sqlstate}, {e.exception.__repr__()}, detail: {detail}"
#
#     logger.error(ll)
#
#     return response


async def postgres(req: Request, e: PostgresError) -> PlainTextResponse:
    """Обработчик исключения базы данных - заготовка для обрывов коннектов во время счёта"""
    if isinstance(e, InternalServerError):
        pass
    ll = f'\n\t<~\t\tPydantic validation error: {req.url.path}, {req.scope["endpoint"].__name__}'
    response = PlainTextResponse(content='DatabaseError', status_code=500)

    ll += f"\n\t<≡\t\t{req.method} {req.url.path} processing request ended"
    ll += f"\n\thead\t{format_flatten_dict(dict(response.headers))}"    # заголовки ответа
    ll += f"\n\tdata\t{trunc_str(response.body.decode())}"              # тело ответа

    logger.error(ll)
    return response
