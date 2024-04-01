# -*- coding: utf-8 -*-
import sys
import logging
import yaml

from pydantic import BaseModel, ConfigDict, StrictStr, ValidationError, computed_field
from typing import Literal, ClassVar

from serv.paths import BASE_PATH
from serv.consts import logging_levels

logger = logging.getLogger('boot')


class Uvicorn(BaseModel):
    """ Описание параметра uvicorn в app[_dev].yml """
    model_config = ConfigDict(extra='forbid')  # неописанные параметры запрещены
    LogTypes: ClassVar = Literal['debug', 'info', 'warning', 'error', 'critical']

    # все параметры необязательные, и если опущены, примут значения по умолчанию как здесь указано
    log: LogTypes = 'error'
    workers: int = 1                # количество рабочих процессов = количество_ядер * количество_потоков_ядра + 1
    host: str | None = '0.0.0.0'
    port: int | None = 8000


class APPconfig(BaseModel):
    """ Дата-класс для проверки параметров конфига приложения """
    model_config = ConfigDict(extra='forbid')   # неописанные параметры запрещены
    LogTypes: ClassVar = Literal[
        'd', 't', 'debug', 'i', 'info', 'e', 'error', 'c', 'critical', 'f', 'fatal', 'w', 'warning', 'warn',
        'D', 'T', 'DEBUG', 'I', 'INFO', 'E', 'ERROR', 'C', 'CRITICAL', 'F', 'FATAL', 'W', 'WARNING', 'WARN']

    # все параметры необязательные
    log: LogTypes = 'DEBUG'
    timing: LogTypes = 'CRITICAL'
    log_format: StrictStr = '%(levelname).1s: %(req_id)s: %(filename)s/%(funcName)s(%(lineno)s): %(message)s'
    debug: bool = False     # запускать ли FastAPI в режиме debug
    uvicorn: Uvicorn = Uvicorn()                       # параметр конфига uvicorn - это словарь

    # ============================== Вычисляемые параметры конфига приложений ==========================
    @computed_field
    @property
    def log_int(self) -> int:
        """Преобразует уровень логирования log из строки в Int"""
        return logging_levels.get(self.log.upper(), logging.DEBUG)

    @computed_field
    @property
    def timing_int(self) -> int:
        """Преобразует уровень логирования timing из строки в Int"""
        return logging_levels.get(self.timing.upper(), logging.FATAL)

    def __init__(self):
        """Инициализация класса конфига БД"""
        super().__init__(**self.load_app(self))

    @staticmethod
    def load_app(self) -> dict:
        """Чтение из файла настроек приложения
        При наличии конфига разработчика, продуктовый конфиг игнорируется
        """
        app_yaml_path = BASE_PATH.joinpath(f'config/app_dev.yml')
        if not app_yaml_path.is_file():
            app_yaml_path = BASE_PATH.joinpath(f'config/app.yml')
            if not app_yaml_path.is_file():
                sys.tracebacklimit = 0
                raise FileNotFoundError(f'APP config not found: {app_yaml_path}')
        logger.info(app_yaml_path.name + ' found and will be used for web-application')

        with open(app_yaml_path) as f:  # создаём конфиг-словарь приложения
            app_dict = yaml.safe_load(f).get('app')
            if app_dict is None:
                sys.tracebacklimit = 0
                raise ValueError(f'APP-config has no "app:" section: {app_yaml_path}')

        return app_dict


try:
    cfg = APPconfig()
except ValidationError as e:
    # красиво отформатируем и напечатаем ошибки в конфиге app[_dev].yml
    ll = list()
    for error in e.errors():
        ll.append(f"\t\t\t- {str(error.get('type'))[:16]:<16} "
                  f"{': '.join(error.get('loc')):<20} = {str(error.get('input')):<12} {error.get('msg')}.")
    from warnings import warn_explicit
    warn_explicit("\n" + "\n".join(ll) + "\nError loading APP-config, fix it. Server stopped now...",
                  category=UserWarning, filename='', lineno=-1)
    exit(-2)
