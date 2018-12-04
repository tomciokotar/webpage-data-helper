import os
import shutil
import urllib.error
import uuid
from bs4 import BeautifulSoup
from bson.objectid import ObjectId
from bson.errors import InvalidId
from threading import Thread
from typing import Dict, List
from urllib.request import urlopen, urlretrieve
from webpage_snaps_utils import is_allowed, is_absolute, join_url


class WebpageSnap:
    def __init__(self, url: str, text_elements: List[str], images: List[Dict[str, str]]):
        self.url = url
        self.text_elements = text_elements
        self.images = images


class FetchStatus:
    NotFetched = 'not fetched'
    Fetching = 'fetching'
    Fetched = 'fetched'
    FetchingFailed = 'fetching failed'


def fetch_webpage_snap_content(requested_url):
    try:
        response = urlopen(requested_url)
    except urllib.error.URLError as e:
        return str(e.reason)
    except ValueError:
        return 'incorrect URL'
    else:
        fetched_url = response.geturl()
        soup = BeautifulSoup(response.read(), 'html.parser')
        text_elements = list(filter(is_allowed, soup.find_all(text=True)))
        images = []
        used_image_urls = set()

        for image in soup.find_all('img'):
            image_url = image.get('src')

            if image_url.startswith('//'):
                image_url = 'http:' + image_url

            if not is_absolute(image_url):
                image_url = join_url(fetched_url, image_url)

            if image_url not in used_image_urls:
                used_image_urls.add(image_url)
                images.append({
                    'id': str(uuid.uuid4()),
                    'url': image_url,
                    'status': FetchStatus.NotFetched
                })

        return WebpageSnap(fetched_url, text_elements, images)


class WebpageSnapsManager:
    def __init__(self, webpage_snaps, images_dir):
        self.webpage_snaps = webpage_snaps
        self.images_dir = images_dir

    def fetch_webpage_snap(self, url, snap_id, fetch_images):
        fetch_response = fetch_webpage_snap_content(url)

        if type(fetch_response) is WebpageSnap:
            if fetch_images:
                image_path = self.images_dir + snap_id + '/'
                os.makedirs(image_path, exist_ok=True)

                for image in fetch_response.images:
                    try:
                        urlretrieve(image['url'], image_path + image['id'])
                    except urllib.error.URLError as e:
                        image.update({
                            'status': FetchStatus.FetchingFailed,
                            'error': str(e.reason)
                        })
                    else:
                        image.update({'status': FetchStatus.Fetched})

            self.webpage_snaps.update_one({'_id': ObjectId(snap_id)}, {'$set': {
                'status': FetchStatus.Fetched,
                'text_elements': fetch_response.text_elements,
                'images': fetch_response.images
            }})
        else:
            self.webpage_snaps.update_one({'_id': ObjectId(snap_id)}, {'$set': {
                'status': FetchStatus.FetchingFailed,
                'error': fetch_response
            }})

    def add_webpage_snap(self, url, fetch_images=False):
        snap_template = {
            'url': url,
            'status': FetchStatus.Fetching
        }
        snap_id = str(self.webpage_snaps.insert_one(snap_template).inserted_id)
        Thread(target=self.fetch_webpage_snap, args=(url, snap_id, fetch_images)).start()
        return snap_id

    def get_webpage_snap(self, snap_id):
        try:
            snap = self.webpage_snaps.find_one({'_id': ObjectId(snap_id)}, {'_id': 0})
        except InvalidId:
            return None
        else:
            return snap

    def delete_webpage_snap(self, snap_id):
        if os.path.isdir(self.images_dir + snap_id):
            shutil.rmtree(self.images_dir + snap_id)
        self.webpage_snaps.delete_one({'_id': ObjectId(snap_id)})
