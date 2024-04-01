## Асинхронный API сервер

### Описание
Заготовка для кодирования под бизнес. <br>
Собрана на Python, FastAPI, asyncpg, SQLAlchemy, Pydantic, ASGI uvicorn, httpx<1,2> <br>
> **Основная особенность** - асинхронная обработка http-запросов и запросов к базе данных.
Увеличивает быстродействие в сравнении с последовательной обработкой в 2,5-3 раза, 
если больше ничего не оптимизировать

Лог загрузки:
``` 
EDUCATION-server (uvicorn 0.25.0) started at 25-03-2024 10:51:42, Monday...
I: app_dev.yml found and will be used for web-application
I: db_dev.yml found and will be used for database connect
I: Database initialization started
I: Main parameters:
	log_level        	= timing 50, uvicorn ERROR, logging 10 (DEBUG)
	python           	= 3.11.6 (tags/v3.11.6:8b6ee5b, Oct  2 2023, 14:57:12) [MSC v.1935 64 bit (AMD64)]
	engine           	= FastAPI 0.109.0 (debug False), asyncpg 0.29.0, alchemy 2.0.28
	pydantic         	= 2.6.3
	config_path      	= D:\projects\education\async_api_server\config
	routes_quantity  	= 5 (include system=4, v1=1, v2=0)
	server_ver       	= 0.1-00-g0000000
I: Database initialized successfully: 
	drivername       	= postgresql+asyncpg
	username         	= AUlyanoff
	password         	= ************
	host             	= ep-snowy-limit-67291163-pooler.eu-central-1.aws.neon.tech
	port             	= 5432
	database         	= asyncpg
	driver           	= asyncpg
	dialect          	= postgresql
	total_tables_found 	= 3 (mainmenu, posts, users...)
I: 53 loggers created
I: OS Windows, fcntl_win used (files descriptor control system)
I: Server loaded successfully, waiting request...
```


### Установка и запуск

1. **Создать** виртуальное окружение  
`python3 -m venv env3`  

2. **Активировать** виртуальное окружение  
```
# Linux:
source env/bin/activate

# Windows:
env\Scripts\activate.bat
```

3. **Установить** зависимости
`pip install -r requirements.txt`

4. **Запустить**:
`python3 src/app_run.py`

