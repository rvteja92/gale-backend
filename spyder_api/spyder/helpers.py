import re
import requests
import logging
import queue

from requests import session


from django.core.cache import caches

from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse


logger = logging.getLogger('gale')
typeparser = re.compile(r'(?P<type>\w+)/(?P<sub_type>\w+).*')
cache = caches['default']


def validate_url(url):
    # logger.debug('Validating url: {0}'.format(url))
    try:
        parsed = urlparse(url)
        return parsed.scheme in ('http', 'https')

    except:
        return False


def is_html_url(url):
    cache_key = 'is_html({0})'.format(url)
    try:
        # logger.debug('Validating html type for url: {0}'.format(url))
        cached_response = cache.get(cache_key)
        if cached_response is not None:
            logger.debug('Html url - Cache hit')
            return cached_response

        response = requests.head(url)
        content_type = response.headers['content-type']
        match = typeparser.match(content_type)
        if match:
            matchdict = match.groupdict()
            is_html = (matchdict['type'] == 'text' and
                       matchdict['sub_type'] == 'html')
            cache.set(cache_key, is_html)
            return is_html

        cache.set(cache_key, False)
        return False

    except:
        # logger.debug('Could not validate html type for url: {0}'.format(url))
        cache.set(cache_key, False)
        return False


def is_image_url(url):
    cache_key = 'is_image({0})'.format(url)
    try:
        # logger.debug('Validating image type for url: {0}'.format(url))
        cached_response = cache.get(cache_key)
        if cached_response is not None:
            logger.debug('Image url - Cache hit')
            return cached_response

        response = requests.head(url)
        content_type = response.headers['content-type']
        match = typeparser.match(content_type)
        if match:
            matchdict = match.groupdict()
            is_image = matchdict['type'] == 'image'
            cache.set(cache_key, is_image)
            return is_image

        cache.set(cache_key, False)
        return False

    except:
        # logger.debug('Could not validate image type for url: {0}'.format(url))
        cache.set(cache_key, False)
        return False


def normalize_url(url, root_url=''):
    if root_url:
        if not url.startswith('http'):
            url = urljoin(root_url, url)

    if validate_url(url):
        return url


def find_tags(html, tag):
    return []


class TagExtractor(HTMLParser):
    def __init__(self, *args, **kwargs):
        self.filter_tags = kwargs.pop('tags')
        self.root_url = kwargs.pop('root_url', '')
        self.url_attrs = {
            'href': is_html_url,
            'src': is_image_url
        }
        self.parsed_data = {
            tag: []
            for tag in self.filter_tags
        }
        super(TagExtractor, self).__init__(*args, **kwargs)

    # def feed(self, data):
    #     return super().feed(data)

    def clean_attrs(self, attrs):
        attrs = dict(attrs)
        cleaned_attrs = {}
        for key in self.url_attrs:
            if key in attrs:
                normalized_url = normalize_url(attrs[key], self.root_url)
                if normalized_url:
                    cleaned_attrs[key] = normalized_url

        # attrs.update(cleaned_attrs)
        return cleaned_attrs

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in self.filter_tags:
            cleaned_attrs = self.clean_attrs(attrs)
            self.parsed_data[tag].append(cleaned_attrs)

    def handle_startendtag(self, tag, attrs):
        if tag in self.filter_tags:
            cleaned_attrs = self.clean_attrs(attrs)
            self.parsed_data[tag].append(cleaned_attrs)


def extract_tags(html, url='', tag_list=[]):
    extractor = TagExtractor(tags=tag_list, root_url=url)
    extractor.feed(html)
    return extractor.parsed_data


class Crawler(object):
    def __init__(self, url, depth):
        self.url = url
        self.depth = depth
        self.visited_urls = set([])
        self.images = set([])
        self.href_queue = queue.Queue()
        self.href_queue.put((0, self.url))

    def extract_tags(self, html, url=''):
        logger.debug('Parsing HTML')
        # logger.debug(html)
        extractor = TagExtractor(tags=['a', 'img'], root_url=url)
        extractor.feed(html)
        # logger.debug(extractor.parsed_data)
        return extractor.parsed_data

    def tag_data(self, url):
        cache_key = 'tag_extract({0})'.format(url)
        cached_response = cache.get(cache_key)
        if cached_response is not None:
            logger.debug('Extracting tags - Cache hit')
            return cached_response

        # logger.debug('Getting tag data for url {0}'.format(url))
        response = requests.get(url)
        extracted_tags = self.extract_tags(response.text, url)
        cache.set(cache_key, extracted_tags)
        return extracted_tags

    def crawl(self, url=None, depth=0):
        logger.debug('depth: {0}, self.depth: {1}'.format(depth, self.depth))
        if depth > self.depth:
            return list(self.images)

        if url is None:
            url = self.url

        if is_html_url(url):
            tag_data = self.tag_data(url)
            # TODO: Store tag_data data to database

            for img_tag in tag_data.get('img', []):
                if is_image_url(img_tag['src']):
                    self.images.add(img_tag['src'])

            self.visited_urls.add(url)
            for html_tag in tag_data.get('a', []):
                hyperlink = html_tag.get('href', '')
                if hyperlink not in self.visited_urls:
                    self.crawl(hyperlink, depth + 1)

        return list(self.images)

    # def _crawl(self, url=None, depth=0):
    #     logger.debug('depth: {0}, self.depth: {1}'.format(depth, self.depth))
    #     if depth > self.depth:
    #         return

    #     if url is None:
    #         url = self.url

    #     if is_html_url(url):
    #         tag_data = self.tag_data(url)
    #         # TODO: Store tag_data data to database

    #         for img_tag in tag_data.get('img', []):
    #             if is_image_url(img_tag['src']):
    #                 self.images.add(img_tag['src'])

    #         self.visited_urls.add(url)
    #         for html_tag in tag_data.get('a', []):
    #             hyperlink = html_tag.get('href', '')
    #             if hyperlink not in self.visited_urls:
    #                 self.href_queue.put((depth + 1, hyperlink))

    # def crawl(self):
    #     while not self.href_queue.empty():
    #         depth, hyperlink = self.href_queue.get()
    #         self._crawl(hyperlink, depth)

    #     return list(self.images)
