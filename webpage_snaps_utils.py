import re
from urllib.parse import urlparse


def is_allowed(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    elif element in [' ', '\n']:
        return False
    return True


def is_absolute(url):
    return bool(urlparse(url).netloc)


def join_url(abs_url, path):
    if not abs_url.endswith('/'):
        abs_url += '/'
    if path.startswith('/'):
        path = path[1:]
    return abs_url + path
