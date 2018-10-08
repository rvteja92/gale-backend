from html.parser import HTMLParser
from urllib.parse import urljoin


def validate_url(url):
    return True


def normalize_url(url, root_url=''):
    if root_url:
        if not url.startswith('http'):
            url = urljoin(root_url, url)
    return url


def find_tags(html, tag):
    return []


class TagExtractor(HTMLParser):
    def __init__(self, *args, **kwargs):
        self.filter_tags = kwargs.pop('tags')
        self.root_url = kwargs.pop('root_url', '')
        self.url_attrs = ['href', 'src']
        self.parsed_data = {
            tag: []
            for tag in self.filter_tags
        }
        super(TagExtractor, self).__init__(*args, **kwargs)

    def clean_attrs(self, attrs):
        attrs = dict(attrs)
        cleaned_attrs = {
            key: normalize_url(attrs[key], self.root_url)
            for key in self.url_attrs if key in attrs
        }
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
