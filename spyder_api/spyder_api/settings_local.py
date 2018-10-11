DEBUG = True

ALLOWED_HOSTS = []


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'gale',
#         'USER': 'galeuser',
#         'PASSWORD': 'galeuser',
#         'HOST': 'localhost',
#     }
# }

CORS_ORIGIN_WHITELIST = (
    'localhost:4200',
    '127.0.0.1:4200'
)
