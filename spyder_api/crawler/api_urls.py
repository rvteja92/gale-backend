from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^crawl/', views.CrawlView.as_view())
]
