import json
import unittest
from unittest.mock import patch
import app
from webpage_snaps_manager import WebpageSnapsManager


retrieved_image_ids = set()
test_webpages_dir = 'test_webpages/'


class MockResponse:
    def __init__(self, data, webpage_name):
        self.data = data
        self.webpage_name = webpage_name

    def geturl(self):
        return 'http://' + self.webpage_name

    def read(self):
        return self.data


def mocked_urlopen(webpage_name):
    try:
        file = open(test_webpages_dir + webpage_name, 'r')
    except IOError:
        raise ValueError
    else:
        response = MockResponse(file.read(), webpage_name)
        file.close()
        return response


def mocked_urlretrieve(_, image_path):
    retrieved_image_ids.add(image_path.split('/')[-1])


def mocked_send_from_directory(_, image_id):
    if image_id in retrieved_image_ids:
        return 'OK'
    else:
        return 'incorrect image'


def mocked_thread(target, args):
    class MockThread:
        def start(self):
            target(*args)

    return MockThread()


class TestWebpageSnaps(unittest.TestCase):
    def setUp(self):
        self.snaps_collection = app.db['test_webpage_snaps']
        retrieved_image_ids.clear()
        app.snaps_manager = WebpageSnapsManager(self.snaps_collection, app.images_dir)
        app.app.testing = True
        self.app = app.app.test_client()

    def tearDown(self):
        self.snaps_collection.drop()

    @patch('webpage_snaps_manager.urlopen', side_effect=mocked_urlopen)
    @patch('webpage_snaps_manager.urlretrieve', side_effect=mocked_urlretrieve)
    @patch('app.send_from_directory', side_effect=mocked_send_from_directory)
    @patch('webpage_snaps_manager.os.makedirs')
    @patch('webpage_snaps_manager.os.path.isdir', return_value=False)
    @patch('webpage_snaps_manager.shutil.rmtree')
    @patch('webpage_snaps_manager.Thread', side_effect=mocked_thread)
    def test_webpage_snaps(self, *_):
        assert b'URL was not found' in self.app.get('/v1/webpage-snaps/nothing').data
        assert b'404 Not Found' in self.app.get('/v1/webpage-snap').data
        assert b'method is not allowed' in self.app.get('/v1/webpage-snaps').data

        rv_post_wrong_url = self.app.post('/v1/webpage-snaps', json=dict(url='abcd'))
        wrong_url_id = json.loads(rv_post_wrong_url.data)['snap_id']
        wrong_url_data = json.loads(self.app.get('/v1/webpage-snaps/' + wrong_url_id).data)
        assert 'fetching failed' in wrong_url_data['status']
        assert 'incorrect URL' in wrong_url_data['error']

        rv_post_wp = self.app.post('/v1/webpage-snaps', json=dict(url='wp', fetch_images=True))
        assert len(retrieved_image_ids) == 48
        assert b'snap_id' in rv_post_wp.data

        rv_post_onet = self.app.post('/v1/webpage-snaps', json=dict(url='onet', fetch_images=True))
        assert len(retrieved_image_ids) == 202
        assert b'snap_id' in rv_post_onet.data

        rv_post_google = self.app.post('/v1/webpage-snaps', json=dict(url='google'))
        assert len(retrieved_image_ids) == 202
        assert b'snap_id' in rv_post_google.data

        wp_id = json.loads(rv_post_wp.data)['snap_id']
        onet_id = json.loads(rv_post_onet.data)['snap_id']
        google_id = json.loads(rv_post_google.data)['snap_id']

        wp_data = json.loads(self.app.get('/v1/webpage-snaps/' + wp_id).data)
        onet_data = json.loads(self.app.get('/v1/webpage-snaps/' + onet_id).data)
        google_data = json.loads(self.app.get('/v1/webpage-snaps/' + google_id).data)

        assert len(wp_data['text_elements']) == 299
        assert len(onet_data['text_elements']) == 825
        assert len(google_data['text_elements']) == 54

        assert 'fetched' in json.loads(self.app.get('/v1/webpage-snaps/' + wp_id + '/info').data).get('status')

        assert len(json.loads(self.app.get('/v1/webpage-snaps/' + wp_id + '/images').data)) == 48
        assert len(json.loads(self.app.get('/v1/webpage-snaps/' + google_id + '/images').data)) == 3

        url = 'http://google/google_pliki/tia.png'
        assert url in json.loads(self.app.get('/v1/webpage-snaps/' + google_id + '/images').data)[0].get('url')

        assert 'not fetched' in json.loads(self.app.get('/v1/webpage-snaps/' + google_id + '/images').data)[0].get('status')

        assert 'vod offer' in json.loads(self.app.get('/v1/webpage-snaps/' + onet_id + '/text').data)[10]

        assert b'404 Not Found' in self.app.get('/v1/webpage-snaps/' + wp_id + '/images/').data
        assert b'URL was not found' in self.app.get('/v1/webpage-snaps/' + wp_id + '/images/abcd').data

        image_id = wp_data['images'][15]['id']
        url = 'http://wp/wp_pliki/a_023.jpeg'
        assert b'OK' in self.app.get('/v1/webpage-snaps/' + wp_id + '/images/' + image_id).data
        assert url in json.loads(self.app.get('/v1/webpage-snaps/' + wp_id + '/images/' + image_id + '/info').data).get('url')


if __name__ == '__main__':
    unittest.main()
