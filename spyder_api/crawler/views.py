from django.shortcuts import render

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Entry
from .serializers import ImageDataSerializer, UrlRequestSerializer

from spyder.helpers import Crawler


class CrawlView(APIView):
    def post(self, request):
        serailizer = UrlRequestSerializer(data=request.data)
        if serailizer.is_valid():
            requested_url = serailizer.data['url']
            crawler = Crawler(requested_url, serailizer.data['depth'])

            # entry = Entry.objects.get_or_create(url=requested_url)[0]
            # entry.crawl(serailizer.html, serailizer.data['depth'])
            return Response({
                'status': 'success',
                # 'data':  ImageDataSerializer(entry).data
                'images': crawler.crawl()
            })

        else:
            return Response({
                'status': 'invalid',
                'data': serailizer.errors
            })
