# Foodgram [![Main Foodgram workflow](https://github.com/the-world-at-large/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/the-world-at-large/foodgram-project-react/actions/workflows/main.yml)

Foodgram - это онлайн-сервис для создания, поиска и сохранения рецептов. Здесь вы можете найти разнообразные блюда, добавить их в избранное, а также поделиться своими кулинарными шедеврами с другими пользователями.

## Содержание

1. [Установка и запуск проекта](#установка-и-запуск-проекта)
2. [Описание проекта](#описание-проекта)
3. [Инструкция по развертыванию](#инструкция-по-развертыванию)
4. [Пример .env файла](#пример-env-файла)
5. [Ссылки](#ссылки)

## Установка и запуск проекта

Для запуска проекта на вашем локальном компьютере выполните следующие шаги:

1. Клонируйте репозиторий на локальную машину:

    ```
    git clone https://github.com/the-world-at-large/foodgram.git
    ```

2. Перейдите в папку проекта:

    ```
    cd foodgram
    ```

3. Установите зависимости из файла requirements.txt:

    ```
    pip install -r requirements.txt
    ```

4. Примените миграции:

    ```
    python manage.py migrate
    ```

5. Создайте суперпользователя:

    ```
    python manage.py createsuperuser
    ```

6. Запустите сервер разработки:

    ```
    python manage.py runserver
    ```

Теперь вы можете открыть [localhost:8000](http://localhost:8000) в вашем браузере и начать использовать Foodgram!

## Описание проекта

Foodgram - это платформа для обмена рецептами и ингредиентами. Основные функции проекта включают в себя:

- Поиск и просмотр рецептов различных блюд.
- Возможность добавления рецептов в избранное.
- Создание собственных рецептов с указанием ингредиентов и тегов.
- Возможность подписки на других пользователей и просмотра их рецептов.

## Инструкция по развертыванию

1. Установите Docker и Docker Compose на вашем компьютере.
2. Склонируйте репозиторий на вашу локальную машину:

    ```
    git clone https://github.com/the-world-at-large/foodgram.git
    ```

3. Перейдите в папку проекта:

    ```
    cd foodgram
    ```

4. Создайте файл .env и заполните его данными, указанными в примере ниже.
5. Запустите Docker Compose:

    ```
    docker-compose up -d
    ```

6. Примените миграции:

    ```
    docker-compose exec web python manage.py migrate
    ```

7. Соберите статику:

    ```
    docker-compose exec web python manage.py collectstatic --no-input
    ```

Теперь вы можете открыть [localhost](http://localhost:80) в вашем браузере и начать использовать Foodgram!

## Пример .env файла

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=your_database_name
POSTGRES_USER=your_postgres_username
POSTGRES_PASSWORD=your_postgres_password
DB_HOST=db
DB_PORT=5432
SECRET_KEY=your_django_secret_key
DEBUG=False
```

![Ура!](https://private-user-images.githubusercontent.com/122881387/303664505-6d18f643-f6c0-44f4-b796-91ce0ee1004f.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MDc0ODY2NTcsIm5iZiI6MTcwNzQ4NjM1NywicGF0aCI6Ii8xMjI4ODEzODcvMzAzNjY0NTA1LTZkMThmNjQzLWY2YzAtNDRmNC1iNzk2LTkxY2UwZWUxMDA0Zi5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjQwMjA5JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI0MDIwOVQxMzQ1NTdaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT03NGNhMGE5Y2NiM2Y5OWNhNmI0MjA3ZThkNzZmYmU5MzI3MjhiOGFkYTgzZDM2OGJkYzMzMmEwOTdiMWEzY2Y3JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZhY3Rvcl9pZD0wJmtleV9pZD0wJnJlcG9faWQ9MCJ9.Xu6nx8XR8HlvNktwmN6zEGSOY0Zhom5rud9Cp_yQeYw)

## Ссылки

- [Foodgram на GitHub](https://github.com/the-world-at-large/foodgram-project-react)
- [Развернутый проект](http://sweetfoodgram.hopto.org)

## Автор

Автор: [the-world-at-large](https://github.com/the-world-at-large)

## Лицензия

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
