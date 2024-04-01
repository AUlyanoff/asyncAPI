#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from json import loads


def tojson(verifiable: str | bytes | bytearray) -> list | dict | None:
    """Попытка загрузить json"""
    """Возвращает json при успехе или None, если json некорректный.
    """
    try:
        result = loads(verifiable)
    except ValueError:
        result = None
    except TypeError as e:
        print(f"({tojson.__doc__}) - Неверный тип аргумента, ожидались строка, байты или массив байт {verifiable}\n{e}")
        raise
    except Exception as e:
        result = None
        print(f"({tojson.__doc__}) - Неожиданная ошибка при разборе json {verifiable}\n{e}")

    return result
