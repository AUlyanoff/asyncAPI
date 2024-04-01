# -*- coding: utf-8 -*-
import logging

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from config.db_mdl import db_cfg

boot = logging.getLogger('boot')
boot.info('Database initialization started')

db_url = URL.create('postgresql+asyncpg',
                    database=db_cfg.name,
                    username=db_cfg.user,
                    password=db_cfg.password,
                    host=db_cfg.host,
                    port=db_cfg.port,
                    )
async_engine = create_async_engine(db_url,                              # куда и к кому подключаться
                                   # echo=True,                          # логировать команды SQL
                                   pool_size=db_cfg.pool_size,          # размер пула соединений
                                   max_overflow=db_cfg.pool_overflow,   # на сколько можно превысить размер пула
                                   echo_pool=True,                      # логировать ведение пула
                                   hide_parameters=True,                # подавление вывода параметров SQL
                                   )
async_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
