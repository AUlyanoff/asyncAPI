# -*- coding: utf-8 -*-
import sys
from datetime import datetime
import logging

from asyncpg import InternalServerError
from sqlalchemy import inspect, insert
from sqlalchemy.ext.asyncio import AsyncConnection

from config.db_mdl import db_cfg
from config.app_mdl import cfg
from database.db_init import async_engine, boot, db_url
from database.tables import meta, main_menu, users, posts

logger = logging.getLogger(__name__)


# Dependency для эндпойнтов
async def get_conn() -> AsyncConnection:
    """Получение коннекта"""
    async with async_engine.connect() as conn:
        yield conn   # будет стоять в этой точке до освобождения коннекта, после чего контекстный менеджер его закроет


async def db_closed():
    """Очистка пула коннектов"""
    await async_engine.dispose()


async def db_init():
    """Пытаемся связаться с базой и залогировать параметры успешной попытки"""
    try:
        await upload_demo(forced=True)
        table_names = await async2sync(get_table_names)
    except InternalServerError as e:
        if e.sqlstate == 'XX000':
            if 'password authentication failed' in getattr(e, "message", ""):
                boot.info('Check host, user or password...')
                sys.tracebacklimit = 0  # страусов не пугать, пол бетонный
            elif 'database ' + db_cfg.name + ' does not exist' in getattr(e, "message", "").replace('"', ''):
                boot.info('Check DB name...')
                sys.tracebacklimit = 0
        raise
    except TimeoutError as e:
        boot.info(f'Timeout with DB-connecting, may be wrong port? Check db_url={db_url} {e}')
        sys.tracebacklimit = 0
        raise

    # красивое логирование параметров базы
    _dict = db_url._asdict()
    _dict.pop('query', None)
    _dict.update(
        password=len(_dict['password']) * '*',
        driver=async_engine.driver,
        dialect=async_engine.dialect.name,
        total_tables_found=f'{len(table_names)} ({", ".join(table_names[:5])}...)',
    )
    boot.info(f'Database initialized successfully: ' + ''.join([f'\n\t{k:<16} \t= {v}' for k, v in _dict.items()]))

    return None


def get_table_names(connection):
    """Читаем список всех таблиц"""
    inspector = inspect(connection)
    db_table_names = inspector.get_table_names()
    return db_table_names


async def async2sync(sync_func):
    """ Inspector асинхронно не работает, см. https://docs.sqlalchemy.org/en/20/errors.html#no-inspection-available
        Поэтому вызываем синхронную сущность из асинхронного коннекта синхронным методом .run_sync
    """
    async with async_engine.connect() as conn:
        result = await conn.run_sync(sync_func)
    return result


async def upload_demo(forced=False):
    """ Заполнение таблиц демо-данными
        forced=True приводит к предварительному уничтожению базы drop_all
    """
    logger.info(f'Upload demo data started, forced={forced}')

    async with async_engine.begin() as conn:
        if forced:
            await conn.run_sync(meta.drop_all)          # Убить все таблицы в базе
            logger.info(f'All database tables dropped...')
        await conn.run_sync(meta.create_all)            # Создать все таблицы в базе (пустые)

        await conn.execute(
            insert(main_menu),
            [
                {'title': 'Главная', 'url': '/'},
                {'title': 'Добавить статью', 'url': '/add_post'},
                {'title': 'Авторизация', 'url': '/login'},
                {'title': 'Донаты', 'url': '/donate'},
            ]
        )

        await conn.execute(
            insert(users),
            [
                {'name': 'Lee Ji-Eun', 'email': 'iu@ya.ru', 'time': datetime.now(), 'avatar': None,
                 'psw': 'pbkdf2:sha256:600000$E6zeNcWAdMGRxtAs$7dde9af9ea97e3b978e5e40a89d0e40536f7e199079f29b9be85986a1608aaa8'},
                {'name': 'Uam12345', 'email': 'u@ya.ru', 'time': datetime.now(), 'avatar': None,
                 'psw': 'pbkdf2:sha256:600000$E6zeNcWAdMGRxtAs$7dde9af9ea97e3b978e5e40a89d0e40536f7e199079f29b9be85986a1608aaa8'},
                {'name': 'Sil12345', 'email': 's@ya.ru', 'time': datetime.now(), 'avatar': None,
                 'psw': 'pbkdf2:sha256:600000$E6zeNcWAdMGRxtAs$7dde9af9ea97e3b978e5e40a89d0e40536f7e199079f29b9be85986a1608aaa8'},
            ]
        )

        await conn.execute(
            insert(posts),
            [
                {'title': 'Про FastAPI', 'url': 'framework-fastapi-intro', 'time': datetime.now(),
                 'text': '<p>FastAPI — это асинхронный веб-фреймворк для языка Python, который предоставляет '
                         'минимальный набор инструментов для создания веб-приложений. <br>На нём можно сделать и '
                         'лендинг, и многостраничный сайт с кучей плагинов и сервисов. <br>Не фреймворк, а мечта!'},
                {'title': 'Про SQLAlchemy', 'url': 'framework-sqlalchemy-intro', 'time': datetime.now(),
                 'text': 'Сила SQLAlchemy — в её ORM. Расшифровывается как object relational mapper, или '
                         '«объектно-реляционное отображение». <br>ORM позволяет управлять базами данных с помощью '
                         'методов объектов в коде и при этом не использовать SQL-запросы. <br>На самом деле это очень '
                         'удобно, так как позволяет писать привычный код, не переключаясь на SQL.'},
                {'title': 'Про Python', 'url': 'python-intro', 'time': datetime.now(),
                 'text': 'Python — это скриптовый язык программирования.     <br>Он универсален, поэтому подходит для '
                         'решения разнообразных задач и для многих платформ: начиная с iOS и Android и заканчивая '
                         'серверными операционными системами. <br>Это интерпретируемый язык, а не компилируемый, '
                         'как C++ или Java. Программа на Python представляет собой обычный текстовый файл.'},
                {'title': 'Про API', 'url': 'about_api', 'time': datetime.now(),
                 'text': 'К этому сайту можно обращаться через api:<br>'
                         '/api/v1/users/count<br>'
                         '/api/v1/users/list<br>'
                         'Это неплохой пример, т.к. любое api в конце концов сводится к вычислениями над базой.'},
            ]
        )

# # Dependency для эндпойнтов
# from database.init import async_session
# from sqlalchemy.ext.asyncio import AsyncSession
# async def get_session() -> AsyncSession:
#     """Получение сессии"""
#     async with async_session() as session:
#         yield session   # будет стоять в этой точке до освобождения сессии, после чего контекстный менеджер её закроет
