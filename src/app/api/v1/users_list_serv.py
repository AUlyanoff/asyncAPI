import logging

from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import select
from database.tables import users
from pydantic import BaseModel, PositiveInt

logger = logging.getLogger(__name__)


async def get_users_list(conn: AsyncConnection):
    """Получить список зарегистрированных пользователей"""
    result = await conn.execute(select(users))
    return result.fetchall()


def serialize(table):
    """Сериализация таблицы в json"""
    list_dicts = list()
    if table is not None:
        for row in table:
            row_dict = row._asdict()    # преобразование mapping-объектов Алхимии в словари
            row_dict.pop('avatar', None)
            row_dict.pop('psw', None)
            if row_dict.get('time'): row_dict['time'] = row_dict.get('time').isoformat()[:-3]+'Z'
            list_dicts.append(row_dict)
    return list_dicts


class filterFields(BaseModel):
    uid: str
    title: str
    versionName: str
    versionCode: PositiveInt
    enabled: bool
