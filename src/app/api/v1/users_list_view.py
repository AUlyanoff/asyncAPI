import logging
from typing import List
from fastapi.responses import JSONResponse
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncConnection
from database.core import get_conn


from app.api.v1.routes import v1
from app.api.v1.users_list_serv import get_users_list, serialize, filterFields
from serv.log_utils import trunc_str

logger = logging.getLogger(__name__)


@v1.post("/users/list")
async def users_list(request: Request, filters: List[filterFields], conn: AsyncConnection = Depends(get_conn)):
    """Возвращает список зарегистрированных юзеров"""
    api_path = request.url.path  # путь вызова API
    logger.debug(f"\n\t=>\t\t{api_path} ({users_list.__doc__}) started..."
                 f"\n\tbody\t[{trunc_str(', '.join([str(flt.dict()) for flt in filters]))}]")

    table_result = await get_users_list(conn)
    dict_result = serialize(table_result)

    response, status = {"data": dict_result}, 200
    ll = f"\n\t<=\t\t{api_path}, HTTP={status} ended\n\tresp\t{trunc_str(response)}"
    logger.debug(ll) if 199 < status < 300 else logger.error(ll)

    return JSONResponse(response, status_code=status)
