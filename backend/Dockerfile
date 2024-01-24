FROM python:3.9
WORKDIR /app
COPY requirements.txt .
# Обновить pip, чтобы проблем не было при установке.
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]
# Для прям детальнейшей отладки.
#CMD [ "python", "./manage.py runserver 0.0.0.0:8000 --settings=foodgram.settings"]