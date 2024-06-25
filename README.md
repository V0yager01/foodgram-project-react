# FoodGram
## Описание
FoodGram проект, позволяющий пользователям находить и делиться разнообразными рецептами блюд. 

## Технологии:
* HTML
* CSS
* JavaScript
* Python
* Django
* React
* Docker.

## Запуcк
Для запуска проекта воспользуемся Linux(Ubuntu)
### Клонирование
Клонируйте репозиторий
```
git@github.com:ponyk1ller/foodgram-project-react.git
```
### Подготовка виртуального окружения
Создаем окружения для проекта
```
sudo nano .env
```
```
POSTGRES_DB=kittygram
POSTGRES_USER=kittygram_user
POSTGRES_PASSWORD=kittygram_password
DB_NAME=kittygram

POSTGRES_DB=food
POSTGRES_USER=food_user
POSTGRES_PASSWORD=food_password
DB_NAME=food

DB_HOST=db
DB_PORT=5432

SECRET_KEY='SECRET_KEY'

DEBUG = 'True'
ALLOWED_HOSTS = '127.0.0.1'

```
### Запуск Docker compose 
В директории проекта запускаем docker-compose.production.yml
```
sudo docker compose up -f docker-compose.production.yml up -d
```
### Подготовка Django
Выполням миграцию и загружаем статику бэкенда.
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
Также у вас есть возможно загрузить в базу готовый список продуктов.
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py load_csv
```
## Конфигурационные файлы
Во время разработки рекомендуется использовать **docker-compose.yml**, где образы билдятся при каждом запуске.
В продакшене использовать **docker-compose.production.yml** для получения готовых образов с Docker Hub.

## Статус
![Workflow Status](https://github.com/ponyk1ller/kittygram_final/actions/workflows/main.yml/badge.svg)


## Автор
Халиуллин Ильяс
