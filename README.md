# Cat Charity Fund

## Описание

Сервис для благотворительных взносов в Фонд Поддержки Котиков.

## Технологии

- [Python v3.9](https://docs.python.org/3.9/)
- [FastApi v0.78](https://fastapi.tiangolo.com/)
- [Pydantic v1.9](https://docs.pydantic.dev/)
- [SQLAlchemy v1.4](https://docs.sqlalchemy.org/en/14/)
- [aiosqlite v0.17](https://aiosqlite.omnilib.dev/en/v0.17.0/)
- [Alembic v1.7](https://alembic.sqlalchemy.org/)
- [Aiogoogle v5.6](https://aiogoogle.readthedocs.io/)

## Запуск проекта на Linux

- Склонируйте репозиторий и перейдите в директорию проекта

```shell
git clone https://github.com/mign0n/cat_charity_fund.git && cd cat_charity_fund
```

- Установите и активируйте виртуальное окружение

```shell
python -m venv venv && source venv/bin/activate
```

- Установите зависимости из файла requirements.txt

```shell
pip install -r requirements.txt
```

- Создайте `.env` файл. Для формирования отчета в Google Sheets с помощью 
Google API необходимо заполнить пустые поля данными, полученными при создании 
сервисного аккаунта в Google Cloud Platform.

```shell
cp .env.example .env
```

- Создайте базу данных

```shell
alembic upgrade head
```

- Запустите веб-сервер и перейдите по адресу [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

```shell
uvicorn app.main:app
```

## API

Документация к API досупна по адресам:

- Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Redoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Авторы

- [Олег Сапожников](https://github.com/mign0n)
- [yandex-praktikum](https://github.com/yandex-praktikum)
