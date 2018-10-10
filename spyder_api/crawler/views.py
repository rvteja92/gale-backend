from django.shortcuts import render

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Entry
from .serializers import ImageDataSerializer, UrlRequestSerializer

from spyder.helpers import normalize_url


class CrawlView(APIView):
    def post(self, request):
        serailizer = UrlRequestSerializer(data=request.data)
        if serailizer.is_valid():
            requested_url = serailizer.data['url']
            entry = Entry.objects.get_or_create(url=requested_url)[0]
            entry.crawl(serailizer.html, serailizer.data['depth'])
            return Response({
                'status': 'success',
                'data':  ImageDataSerializer(entry).data
            })

        else:
            return Response({
                'status': 'invalid',
                'data': serailizer.errors
            })
