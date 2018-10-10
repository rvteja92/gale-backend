import logging

import requests

from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.validators import URLValidator

from spyder.helpers import (
    extract_tags,
    validate_url as is_valid_url,
    is_html_url
)


logger = logging.getLogger('gale')


class Entry(models.Model):
    url = models.TextField(unique=True, validators=[URLValidator])
    links = ArrayField(models.TextField(validators=[URLValidator]),
                       blank=True, null=True)
    images = ArrayField(models.TextField(validators=[URLValidator]),
                        blank=True, null=True)
    complete = models.BooleanField(default=False)
    parent = models.ForeignKey('self', related_name='child_links',
                               blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def _crawl_page(self, cached_html=None):
        self.image_data = []
        self.links = []
        if not is_valid_url(self.url):
            return

        if cached_html is None:
            logger.debug('Visiting page: {0}'.format(self.url))
            if is_html_url(self.url):
                response = requests.get(self.url)
                cached_html = response.text
            else:
                return

        parsed_tags = extract_tags(cached_html, self.url, ['a', 'img'])
        self.links = [anchor['href'] for anchor in parsed_tags['a']
                            if 'href' in anchor]
        self.images = [img['src'] for img in parsed_tags['img']
                            if 'src' in img]
        self.image_data = self.images
        self.complete = True
        self.save()

    def crawl(self, cached_html, depth=0, re_parse=False):
        if depth <= 0:
            if self.complete and not re_parse:
                self.image_data = self.images
                return

            self._crawl_page(cached_html)

        else:
            self._crawl_page(cached_html)

            for link in self.links:
                entry = Entry.objects.get_or_create(url=link)[0]
                entry.crawl(None, depth - 1, re_parse)
                self.image_data += entry.image_data
