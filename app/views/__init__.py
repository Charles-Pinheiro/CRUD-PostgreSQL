from flask import Flask, Blueprint, request
from psycopg2.errors import UniqueViolation

bp_animes = Blueprint('animes', __name__, url_prefix='/animes')

from app.services import Anime


def init_app(app: Flask):

    @bp_animes.route('', methods=('GET', 'POST'))
    def get_create():

        if request.method == 'POST':
            data = request.json
            try:
                new_anime = Anime.save(data)
                if type(new_anime) == list:
                    return {
                        'available_keys': [
                            'anime', 'released_date', 'seasons'
                        ],
                        'wrong_keys_sended': new_anime
                    }, 422
                return new_anime, 201
            except UniqueViolation:
                return {'error': 'anime is already exists'}, 422

        if request.method == 'GET':
            animes = Anime.get_all()
            return {'data': animes}, 200


    @bp_animes.get('/<int:anime_id>')
    def filter(anime_id):
        try:
            anime = Anime.get_by_id(anime_id)
            return {'data': [anime]}, 200
        except:
            return {'error': 'Not Found'}, 404


    @bp_animes.patch('/<int:anime_id>')
    def update(anime_id):

        data = request.json
        try:
            updated_anime = Anime.update(anime_id, data)
            if type(updated_anime) == list:
                return {
                    'available_keys': [
                        'anime', 'released_date', 'seasons'
                    ],
                    'wrong_keys_sended': updated_anime
                }, 422
            return updated_anime, 200 
        except:
            return {'error': 'Not Found'}, 404

    @bp_animes.delete('/<int:anime_id>')
    def delete(anime_id):

        try:
            Anime.delete(anime_id)
            return '', 204
        except:
            return {'error': 'Not Found'}, 404

    app.register_blueprint(bp_animes)
