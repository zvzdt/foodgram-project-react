
## Foodgram. Продуктовый помощник.

«Продуктовый помощник» - соцсеть, где пользователи могут публиковать свои рецепты, подписываться на публикации других пользователей, добавлять рецепты в «Избранное», скачивать список продуктов, необходимых для приготовления выбранных блюд. Ссылка на сайт: https://dlsib.sytes.net

## Authors

- [@zvzdt](https://www.github.com/zvzdt)


## стэк

Python 3.9, Django 3.2.3, Gunicorn 21.2, Nginx 1.22.1, Docker, Postgres 16.1


## Как развернуть проект:
```
git clone git@github.com:zvzdt/foodgram-project-react.git
```
```
cd foodgram-project-react
```
```
Cоздать и активировать виртуальное окружение:
python3 -m venv env
```
```
Если у вас Linux/macOS
- source env/bin/activate
```
```
Если у вас windows
- source env/scripts/activate
```
```
python3 -m pip install --upgrade pip
```
```
Установить зависимости из файла requirements.txt:
pip install -r requirements.txt
```
```
Перейти в каталог infra
cd foodgram-project-react/infra
```
```
Создать файл .evn для хранения ключей:

SECRET_KEY='указать секретный ключ'
ALLOWED_HOSTS='указать имя или IP хоста'
POSTGRES_DB=foodgram
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_NAME=foodgram
DB_HOST=db
DB_PORT=5432
DEBUG=False
```
```
Запустить docker-compose.production:
docker compose -f docker-compose.production.yml up
```
```
Выполнить миграции:
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```
```
Собрать статику:
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --no-input
```
```
Загрузить ингредиенты в базу данных:
docker compose -f docker-compose.production.yml exec backend python manage.py load_data
```
```
Создать суперпользователя, ввести почту, логин, пароль:
docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

