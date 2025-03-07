# Foodgram [![Main Foodgram workflow](https://github.com/the-world-at-large/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/the-world-at-large/foodgram-project-react/actions/workflows/main.yml)

Foodgram is an online service for creating, searching, and saving recipes. Here, you can discover a variety of dishes, add them to your favorites, and share your culinary masterpieces with other users.

## Contents

1. [Installation and project setup](#installation-and-project-setup)
2. [Project description](#project-description)
3. [Deployment instructions](#deployment-instructions)
4. [Example .env file](#example-env-file)
5. [Links](#links)

## Installation and project setup

To run the project on your local machine, follow these steps:

1. Clone the repository to your local machine:

    ```
    git clone https://github.com/the-world-at-large/foodgram.git
    ```

2. Navigate to the project directory:

    ```
    cd foodgram
    ```

3. Install dependencies from the requirements.txt file:

    ```
    pip install -r requirements.txt
    ```

4. Apply migrations:

    ```
    python manage.py migrate
    ```

5. Create a superuser:

    ```
    python manage.py createsuperuser
    ```

6. Run the development server:

    ```
    python manage.py runserver
    ```

Now you can open [localhost:8000](http://localhost:8000) in your browser and start using Foodgram!

## Project description

Foodgram is a platform for sharing recipes and ingredients. The main features include:

- Searching and viewing recipes for various dishes.
- Adding recipes to favorites.
- Creating your own recipes with specified ingredients and tags.
- Following other users and viewing their recipes.

## Deployment instructions

1. Install Docker and Docker Compose on your computer.
2. Clone the repository to your local machine:

    ```
    git clone https://github.com/the-world-at-large/foodgram.git
    ```

3. Navigate to the project directory:

    ```
    cd foodgram
    ```

4. Create a .env file and fill it with the required data, as shown in the example below.
5. Start Docker Compose:

    ```
    docker-compose up -d
    ```

6. Apply migrations:

    ```
    docker-compose exec web python manage.py migrate
    ```

7. Collect static files:

    ```
    docker-compose exec web python manage.py collectstatic --no-input
    ```

Now you can open [localhost](http://localhost:80) in your browser and start using Foodgram!

## Example .env file

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


![Hooray!](https://github.com/the-world-at-large/foodgram-project-react/assets/122881387/6d18f643-f6c0-44f4-b796-91ce0ee1004f)

## Links

- [Foodgram on GitHub](https://github.com/the-world-at-large/foodgram-project-react)
- [Deployed project](http://sweetfoodgram.hopto.org)

## Author

Author: [the-world-at-large](https://github.com/the-world-at-large)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
