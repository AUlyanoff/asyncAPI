# -*- coding: utf-8 -*-
from multiprocessing import freeze_support
import logging
boot = logging.getLogger("boot")  # логер для вывода загрузочной информации
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname).1s: %(message)s', "%Y-%m-%d %H:%M:%S"))
boot.propagate = False  # запрет наследования от родителя, поэтому формат и уровень логера не будут меняться
boot.addHandler(handler)
boot.setLevel(logging.INFO)

if __name__ == "__main__":
    freeze_support()

    from warnings import warn_explicit
    from datetime import datetime
    import uvicorn

    warn_explicit(f"\nEDUCATION-server (uvicorn {uvicorn.__version__}) started at "
                  f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S, %A')}...",
                  category=UserWarning, filename='', lineno=-1)

    from config.app_mdl import cfg
    uvi = cfg.uvicorn

    uvicorn.run("app.app_init:app", host=uvi.host, port=uvi.port, log_level=uvi.log, workers=uvi.workers)
