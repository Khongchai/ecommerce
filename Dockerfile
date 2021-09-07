FROM python:3

ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY requirements.txt /code/

RUN pip install -r requirements.txt
RUN export DJANGO_SETTINGS_MODULE=ecommerce.settings_production \
    && python manage.py migrate \
    && python manage.py loaddata initial_composers.json \
    && python manage.py loaddata initial_compositions.json \
    && python manage.py loaddata initial_dataAfterPurchase.json \
    && python manage.py loaddata initial_product.json \
    && python manage.py runserver 0.0.0.0:8000 

COPY . /code/