DEBUG = True

ALLOWED_HOSTS = []


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gale',
        'USER': 'galeuser',
        'PASSWORD': 'galeuser',
        'HOST': 'localhost',
    }
}
