import requests

from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField

from spyder.helpers import extract_tags


class Entry(models.Model):
    url = models.URLField(unique=True)
    links = ArrayField(models.TextField(), blank=True, null=True)
    images = JSONField(blank=True, null=True)
    complete = models.BooleanField(default=False)
    parent = models.ForeignKey('self', related_name='child_links',
                               blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def crawl(self, cached_html=None, re_parse=False):
        if self.complete and not re_parse:
            return

        if cached_html is None:
            response = requests.get(self.url)
            cached_html = response.text

        parsed_tags = extract_tags(cached_html, self.url, ['a', 'img'])
        self.links = [anchor['href'] for anchor in parsed_tags['a']]
        self.images = [img['src'] for img in parsed_tags['img']]
        self.complete = True
        self.save()
