# -*- coding: utf-8 -*-
import sys
import logging
import yaml

from pydantic import BaseModel, Field, PositiveInt, IPvAnyAddress, ConfigDict, FilePath, StrictStr, AnyUrl, SecretStr, \
    ValidationError
from typing import Literal, Union
from typing_extensions import Annotated

from serv.paths import BASE_PATH

logger = logging.getLogger('boot')


class DBconfig(BaseModel):
    """ Дата-класс для проверки значений параметров конфига базы """
    # разрешим приведение типов numbers -> str и запретим неописанные параметры
    model_config = ConfigDict(coerce_numbers_to_str=True, extra='forbid')

    # обязательные параметры
    db_schema: StrictStr                                    # строгая строка - запретим приведение типов numeric -> str
    user: StrictStr
    password: Union[str, int]
    host: Union[IPvAnyAddress, AnyUrl, StrictStr]           # IP-адрес v4/v6, или любой url, или нецифровая строка
    port: PositiveInt                                       # натуральное число
    name: StrictStr

    # необязательные параметры, могут отсутствовать в конфиге, и тогда примут значения по умолчанию, как здесь указано
    type: Literal['postgresql', 'PostgreSQL', 'Mock', 'mock'] = 'postgresql'  # перечень возможных значений
    pool_size: Annotated[int, Field(ge=1, le=1999)] = 16
    pool_overflow: Annotated[int, Field(ge=0, le=1999)] = 8
    sslmode: Literal['disable', 'allow', 'prefer', 'require', 'verify-ca', 'verify-full'] = 'disable'
    sslrootcert: FilePath = ''                              # путь существует и является файлом
    sslcert: FilePath = ''
    sslkey: FilePath = ''

    def __init__(self):
        """Инициализация класса конфига БД"""
        super().__init__(**self.load_db())

    @staticmethod
    def load_db():
        """Чтение из файла настроек базы
        При наличии конфига разработчика, продуктовый конфиг игнорируется
        """
        db_yaml_path = BASE_PATH.joinpath('config/db_dev.yml')
        if not db_yaml_path.is_file():
            db_yaml_path = BASE_PATH.joinpath('config/db.yml')
            if not db_yaml_path.is_file():
                sys.tracebacklimit = 0
                raise FileNotFoundError(f'DB config not found: {db_yaml_path}')

        logger.info(db_yaml_path.name + ' found and will be used for database connect')

        with open(db_yaml_path) as f:  # создаём конфиг-словарь базы
            db_dict = yaml.safe_load(f).get('db')
            if db_dict is None:
                sys.tracebacklimit = 0
                raise ValueError(f'DB-config has no "db:" section: {db_yaml_path}')

        return db_dict


try:
    db_cfg = DBconfig()
except ValidationError as e:
    # красиво отформатируем и напечатаем ошибки в конфиге db[_dev].yml
    ll = list()
    for error in e.errors():
        ll.append(f"\t\t\t- {str(error.get('type'))[:16]:<16} "
                  f"{': '.join(error.get('loc')):<20} = {str(error.get('input')):<12} {error.get('msg')}.")
    from warnings import warn_explicit
    warn_explicit("\n" + "\n".join(ll) + "\nError loading DB-config, fix it. Server stopped now...",
                  category=UserWarning, filename='', lineno=-1)
    exit(-1)
