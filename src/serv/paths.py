# -*- coding: utf-8 -*-
import os
from pathlib import Path

# определение корня проекта и папки src
BASE_PATH = Path(__file__).resolve().parent.parent.parent
SRC_PATH = Path(__file__).resolve().parent.parent

# установка значения по умолчанию для переменных окружения
os.environ.setdefault("CONF_DIR", str(BASE_PATH.joinpath("config")))
os.environ.setdefault("JSON_DIR", str(SRC_PATH.joinpath("json")))

# определение путей к папкам json и config
config_path = Path(os.environ.get("CONF_DIR"))
json_path = Path(os.environ.get("JSON_DIR"))

xml_schema_path = SRC_PATH.joinpath('xml_schemas')
json_schema_path = SRC_PATH.joinpath('app/android/json_schemas')
