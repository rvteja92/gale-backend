import requests
import logging

from urllib.parse import quote_plus

from rest_framework import serializers

from .models import Entry

from spyder.helpers import normalize_url, validate_url as is_valid_url


logger = logging.getLogger('gale')


class EntrySerializer(serializers.ModelSerializer):
    links = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Entry
        fields = ('url', 'links', 'images', )

    def get_links(self, obj):
        return [url.replace(' ', '+') for url in obj.links]

    def get_images(self, obj):
        return [url.replace(' ', '+') for url in obj.images]


class UrlRequestSerializer(serializers.Serializer):
    url = serializers.URLField()
    depth = serializers.IntegerField(max_value=10, min_value=0)

    def validate_url(self, value):
        return normalize_url(value)

    def validate(self, data):
        url = data['url']
        response = requests.get(url)
        if not response.headers['content-type'].startswith('text/html'):
            logger.debug('Content type: {0}'.format(
                response.headers['content-type']))
            raise serializers.ValidationError('We only support html content')

        self.html = response.text
        return data
