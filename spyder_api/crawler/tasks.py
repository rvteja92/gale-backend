from spyder_api.celery import app

from crawler.models import Entry


@app.task
def update_url(url, data):
    pass
