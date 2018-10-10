import re
import requests
import logging

from requests import session

from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse


logger = logging.getLogger('gale')
typeparser = re.compile(r'(?P<type>\w+)/(?P<sub_type>\w+).*')

def validate_url(url):
    logger.debug('Validating url: {0}'.format(url))
    try:
        parsed = urlparse(url)
        return parsed.scheme in ('http', 'https')

    except:
        return False


def is_html_url(url):
    try:
        logger.debug('Validating html type for url: {0}'.format(url))
        response = requests.head(url)
        content_type = response.headers['content-type']
        match = typeparser.match(content_type)
        if match:
            matchdict = match.groupdict()
            return (matchdict['type'] == 'text' and
                    matchdict['sub_type'] == 'html')

        return False

    except:
        logger.debug('Could not validate html type for url: {0}'.format(url))
        return False


def is_image_url(url):
    try:
        logger.debug('Validating image type for url: {0}'.format(url))
        response = requests.head(url)
        content_type = response.headers['content-type']
        match = typeparser.match(content_type)
        if match:
            matchdict = match.groupdict()
            return matchdict['type'] == 'image'

        return False

    except:
        logger.debug('Could not validate image type for url: {0}'.format(url))
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

    def clean_attrs(self, attrs):
        attrs = dict(attrs)
        cleaned_attrs = {}
        for key in self.url_attrs:
            if key in attrs:
                normalized_url = normalize_url(attrs[key], self.root_url)
                if normalized_url and self.url_attrs[key](normalized_url):
                    cleaned_attrs[key] = normalized_url

        attrs.update(cleaned_attrs)
        return attrs

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in self.filter_tags:
            self.parsed_data[tag].append(self.clean_attrs(attrs))

    def handle_startendtag(self, tag, attrs):
        if tag in self.filter_tags:
            self.parsed_data[tag].append(self.clean_attrs(attrs))


def extract_tags(html, url='', tag_list=[]):
    extractor = TagExtractor(tags=tag_list, root_url=url)
    extractor.feed(html)
    return extractor.parsed_data
