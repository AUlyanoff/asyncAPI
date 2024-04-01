# -*- coding: utf-8 -*-
import logging
import plistlib
import re
from copy import deepcopy
from pprint import pformat
from textwrap import wrap  # разрезает строку на части с переносом целых слов, и складывает эти части в список
from typing import Union, Any

from collections.abc import Iterable

logger = logging.getLogger(__name__)


def format_flatten_dict(d: dict, len_str: int = 170, delimiter='\n\t\t\t'):
    """Данная функция предназначена для форматирования плоских словарей
    Превращает словарь в строку таким образом, что содержимое ключей/значений не разрывается между строками
    Если ключ+значение не помещается в текущую строчку переносит его на следующую
    Если ключ+значение не помещается на целую строчку и входит в перечень разрешённых для обрубания ключей рубит его
    ВНИМАНИЕ: с неплоскими словарями (включающими в качестве значений словари/массивы/сеты и т. д. работает некорректно
    :param d: словарь для форматирования
    :param len_str: максимальная
    :param delimiter: разделитель
    :return: словарь в строковом представлении
    """

    # trunc_keys - ключи словаря, значения которых можно обрубать
    trunc_keys = {'mdm-signature',
                  'x-client-certificate',  # Сертификат mTLS, есть необрезанный отпечаток
                  'cookie',
                  'set-cookie',
                  'x-envoy-peer-metadata',  # Заголовки балансировщика
                  'x-envoy-peer-metadata-id'
                  }
    lines = []
    current_line = ""
    for k, v in d.items():  # итерация по словарю
        if str(k).lower() in trunc_keys:
            v = f'{v[:64]}... cut off, {len(v)} total'
        entry = f"'{k}': '{v}', "
        if len(current_line) + len(entry) < len_str:  # если ключ значение помещаются в строку
            current_line += entry  # добавляем его в текующую строку
        else:  # если не помещаются
            lines.append(current_line)  # предыдущую строку пишем в массив
            current_line = entry  # текущие ключ значение становятся новой строкой
    if current_line:
        lines.append(current_line)
    return '{' + delimiter.join(lines)[:-2] + '}'


def trunc_object(obj: Union[dict, Iterable], max_len: int = 32) -> Union[dict, list, str]:
    """Обёртка над рекурсивной функцией, обрезающей длинные строки в объекте.
    Делает deepcopy объекта для исключения изменения переданного объекта
    """
    cut_keys = {'certificate', 'PayloadContent', 'CheckInURL', 'UnlockToken', 'Payload', 'Icon'}

    def _trunc_object(node: Union[dict, list, str], node_name: str = None) -> Union[dict, list, str]:
        """Рекурсивный обход объекта и сжатие длинных строк."""
        if isinstance(node, dict):
            for field in node.keys():
                node[field] = _trunc_object(node[field], field)
        elif isinstance(node, list):
            for ind, item in enumerate(node):
                node[ind] = _trunc_object(item, node_name)
        elif isinstance(node, str):
            if node_name in cut_keys and len(node) > max_len:
                node = f'{node[:max_len]}... сut off, total: {len(node)}'
        elif isinstance(node, bytes):
            if node_name == 'Payload':
                node = plistlib.loads(node)
                for field in node.keys():
                    node[field] = _trunc_object(node[field], field)

            elif node_name in cut_keys and len(node) > max_len:
                node = f'{node[:max_len]}... сut off, total: {len(node)}'

        return node

    try:
        cuttable_obj = _trunc_object(deepcopy(obj))
    except RecursionError:  # если у объекта слишком много вложенностей, отдаём без преобразований
        cuttable_obj = obj

    return cuttable_obj


def trunc_str(s, len_str=170, amount=16, delimiter='\n\t\t\t', pf: bool = False) -> str:
    """
    Разбиение строкового представления объекта на короткие строки для удобства отображения
    :param s: строка
    :param len_str: максимальная длина строки
    :param amount: максимальное число строк
    :param delimiter: разделитель
    :param pf: использовать ли pformat
    :return: разбитую строку

    при использовании pformat игнорируются все параметры кроме разделителя.
    pformat печатает объекты в столбик, но сильно увеличивает высоту лога.
    в данной функции применяется только к dict
    """

    if isinstance(s, dict):  # если передан словарь
        s = trunc_object(s)  # ищем в нём длинные поля и обрубаем их

        if pf:  # если используется pformat
            res = pformat(s, width=len_str)
            return re.sub('(\n)', delimiter, res)

    if s is not None:       # а есть с чем работать?
        res = str(s) if not isinstance(s, str) else s   # всё что к нам приходит, становится строкой
        lns = len(res)
        if lns > len_str:   # а не слишком короткая?
            chars_left = lns - len_str * amount
            if 0 < chars_left < len_str // 2:   # если не влезло меньше чем пол-строки,
                amount += 1                     # то добавим строчку
            lst = wrap(res, len_str)[:amount]   # режем на куски длиной по len_str, а потом отбрасываем лишнее
            if len_str * amount < lns:          # если не влезли в amount строк, в последней допишем, сколько обрезано
                res = delimiter.join(lst)[:-len(delimiter)]     # от конца строки-результата отрезаем разделители
                res = f'{res}{delimiter}... cut off, {chars_left} characters left!'
            else:
                res = delimiter.join(lst)   # [:-len(delimiter)]
    else:
        res = s
    return res


def to_debug_message(message: Any):
    """Удаление служебных символов и лишних пробелов (два и более подряд заменяются на один)"""
    # s = re.sub(r"\s+", " ", str(message.decode('utf8')))
    s = re.sub(r"\s+", " ", str(message.decode('unicode-escape')))
    return s
