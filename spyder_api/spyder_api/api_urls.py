from django.conf.urls import url, include


urlpatterns = [
    url(r'^crawler/', include('crawler.api_urls'))
]
