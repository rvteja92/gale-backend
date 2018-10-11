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
            page = serailizer.data['page']
            images = crawler.crawl(page)

            return Response({
                'status': 'success',
                # 'data':  ImageDataSerializer(entry).data
                'images': images,
                'complete': crawler.image_count < (page * 20)
            })

        else:
            return Response({
                'status': 'invalid',
                'data': serailizer.errors
            })
