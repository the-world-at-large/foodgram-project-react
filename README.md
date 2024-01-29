# Foodgram

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
    git clone https://github.com/your_usernam/foodgram.git
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
    git clone https://github.com/your_username/foodgram.git
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

Теперь вы можете открыть [localhost](http://localhost) в вашем браузере и начать использовать Foodgram!

## Пример .env файла

DB_ENGINE=django.db.backends.postgresql
DB_NAME=your_database_name
POSTGRES_USER=your_postgres_username
POSTGRES_PASSWORD=your_postgres_password
DB_HOST=db
DB_PORT=5432
SECRET_KEY=your_django_secret_key
DEBUG=1

## Ссылки

- [Foodgram на GitHub](https://github.com/the-world-at-large/foodgram-project-react)
- [Развернутый проект](http://sweetfoodgram.hopto.org)
- [Бейдж GitHub о успешном деплое]()

## Автор

Автор: [the-world-at-large](https://github.com/the-world-at-large)

## Лицензия

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
