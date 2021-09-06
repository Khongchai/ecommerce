from ecommerce.settings import *


DEBUG = False

ALLOWED_HOSTS = ["localhost"]

CORS_ALLOWED_ORIGINS = []

WSGI_APPLICATION = 'ecommerce.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('DATABASE_NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASSWORD'),
        'HOST': "postgresql",
        'PORT': "5432"
        }
}