from flask import Flask, abort, send_from_directory
from flask_restful import Api, Resource, reqparse
from pymongo import MongoClient
from webpage_snaps_manager import WebpageSnapsManager

app = Flask(__name__)
api = Api(app)

images_dir = 'static/images/'

mongo_client = MongoClient('mongodb://mongodb:27017/')
db = mongo_client['resources_db']
snaps_manager = WebpageSnapsManager(db['webpage_snaps'], images_dir)


def get_webpage_snap(snap_id):
    snap = snaps_manager.get_webpage_snap(snap_id)
    if snap is None:
        abort(404)
    return snap


def get_image(snap_id, image_id):
    images = get_webpage_snap(snap_id).get('images')
    if images is None:
        abort(404)

    image = next((image for image in images if image['id'] == image_id), None)
    if image is None:
        abort(404)
    return image


class WebpageSnapListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('url', type=str, required=True, help='No URL provided', location='json')
        self.reqparse.add_argument('fetch_images', type=bool, default=False, location='json')
        super(WebpageSnapListAPI, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        snap_id = snaps_manager.add_webpage_snap(args['url'], args['fetch_images'])
        return {'snap_id': snap_id}, 201


class WebpageSnapAPI(Resource):
    def get(self, snap_id):
        return get_webpage_snap(snap_id)

    def delete(self, snap_id):
        get_webpage_snap(snap_id)
        snaps_manager.delete_webpage_snap(snap_id)
        return '', 204


class WebpageSnapInfoAPI(Resource):
    def get(self, snap_id):
        snap = get_webpage_snap(snap_id)
        return {
            'url': snap.get('url'),
            'status': snap.get('status'),
            'error': snap.get('error')
        }


class TextAPI(Resource):
    def get(self, snap_id):
        return get_webpage_snap(snap_id).get('text_elements')


class ImageListAPI(Resource):
    def get(self, snap_id):
        return get_webpage_snap(snap_id).get('images')


class ImageAPI(Resource):
    def get(self, snap_id, image_id):
        get_image(snap_id, image_id)
        return send_from_directory('../' + images_dir + snap_id + '/', image_id)


class ImageInfoAPI(Resource):
    def get(self, snap_id, image_id):
        image = get_image(snap_id, image_id)
        return {
            'url': image.get('url'),
            'status': image.get('status'),
            'error': image.get('error')
        }


api.add_resource(WebpageSnapListAPI, '/v1/webpage-snaps')
api.add_resource(WebpageSnapAPI, '/v1/webpage-snaps/<string:snap_id>')
api.add_resource(WebpageSnapInfoAPI, '/v1/webpage-snaps/<string:snap_id>/info')
api.add_resource(TextAPI, '/v1/webpage-snaps/<string:snap_id>/text')
api.add_resource(ImageListAPI, '/v1/webpage-snaps/<string:snap_id>/images')
api.add_resource(ImageAPI, '/v1/webpage-snaps/<string:snap_id>/images/<string:image_id>')
api.add_resource(ImageInfoAPI, '/v1/webpage-snaps/<string:snap_id>/images/<string:image_id>/info')

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
