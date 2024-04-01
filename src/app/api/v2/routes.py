# -*- coding: utf-8 -*-
from fastapi import APIRouter
from serv.ep_monitor import EPMonitor

v2 = APIRouter(route_class=EPMonitor)  # класс EPMonitor наблюдает за окончанием ендпойнта, это пред и пост обработка
