# -*- coding: utf-8 -*-
import logging
import sys
import platform

from serv.req_id import ctx_req_id
from serv.consts import color

# logger = logging.getLogger("log_logger")


class CustomFormatter(logging.Formatter):
    """Модифицирует поведение стандартного форматтера, от которого и наследуется"""

    def format(self, record):
        """Красит букву уровня логирования и удаляет переносы строк в логировании Алхимии"""

        if 'sqlalchemy.engine' in record.name:
            record.msg = record.msg.replace('\n', '').replace('\t', ' ').replace('\r', '')

        formatted_record = super().format(record)  # стандартный формат
        pos = 20 if 0 < self._fmt.find('asctime') < 5 else 0  # включено или отключено логирование времени
        painted_letter = color[record.levelno] + formatted_record[pos] + color[0]
        painted_record = formatted_record[:pos] + painted_letter + formatted_record[pos + 1:]

        return painted_record


class InjectingReqID(logging.Filter):
    """Фильтр, добавляющий номер запроса из переменной контекста в строки логов"""
    def filter(self, record) -> bool:
        """record - объект строки логирования"""
        try:
            record.req_id = ctx_req_id.get()  # этот номер сгенерирован во время асинхронного старта обработки запроса
        except LookupError:
            record.req_id = "000000-000"
        return True


def setup_log(logging_level: int, log_format: str) -> None:
    """Установка общих параметров логирования"""
    boot = logging.getLogger("boot")

    # Установка потокового обработчика handler для стандартного вывода stderr
    stdout_handler = logging.StreamHandler(sys.stderr)
    stdout_handler.setFormatter(CustomFormatter(log_format, "%Y-%m-%d %H:%M:%S"))

    # Добавление фильтра, который ничего не фильтрует, но актуализирует req_id из контекста
    add_req_id = InjectingReqID()
    stdout_handler.addFilter(add_req_id)

    # ВАЖНО! если это вдруг не первая установка конфигурации логирования, то нужно передать keyword force=True
    logging.basicConfig(level=logging_level, handlers=[stdout_handler], force=True)

    # получим список всех логеров в системе
    ar = sorted(list(set([logger_name for logger_name in logging.Logger.manager.loggerDict.keys()])))
    boot.info(f"{len(ar)} loggers created")

    # Логирование файловой системы
    os_platform = platform.system()
    if os_platform == "Windows":
        boot.info(f"OS {os_platform}, fcntl_win used (files descriptor control system)")
    else:
        boot.info(f"OS {os_platform}, fcntl used (files descriptor control system)")

    # пространство имён логирования Алхимииб установим для Алхимии тот же уровень, что и приложению
    logging.getLogger('sqlalchemy.engine').setLevel(logging_level)
    logging.getLogger('sqlalchemy.pool').setLevel(logging_level)
