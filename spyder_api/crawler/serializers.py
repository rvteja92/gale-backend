import re
import requests
import logging

from urllib.parse import quote_plus, urlparse

from rest_framework import serializers

from .models import Entry

from spyder.helpers import normalize_url, validate_url as is_valid_url


logger = logging.getLogger('gale')
typeparser = re.compile(r'(?P<type>\w+)/(?P<sub_type>\w+).*')

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
    page = serializers.IntegerField(min_value=1)

    def validate_url(self, value):
        parsed = urlparse(value)
        if parsed.scheme not in ('http', 'https'):
            serializers.ValidationError(
                    'We only support "http" and "https" protocol schemes')

        return value

    def validate(self, data):
        url = data['url']

        try:
            logger.debug('Validating html type for url: {0}'.format(url))
            response = requests.head(url)
            content_type = response.headers['content-type']
            match = typeparser.match(content_type)
            if match:
                matchdict = match.groupdict()
                if (matchdict['type'] == 'text' and
                        matchdict['sub_type'] == 'html'):

                    if matchdict['Content-Length'] > 4 * 1024 * 1024:
                        serializers.ValidationError(
                                'HTML is too long to parse')

                    return data

            serializers.ValidationError(
                'The supplied URL does not serve HTML content')

        except:
            serializers.ValidationError('Failed to retrieve information')

        response = requests.get(url)
        self.html = response.text
        return data


class ImageDataSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = Entry
        fields = ('url', 'images', )

    def get_images(self, obj):
        return obj.image_data
