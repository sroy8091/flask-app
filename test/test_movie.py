import json
import unittest
from datetime import datetime, timedelta

import jwt

import config
from models import User, Movies, Genres, ES
from models.abc import db
from server import server
from util.elastic_utils import movie_mapping


class TestUser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = server.test_client()

    def setUp(self):
        db.create_all()
        self.user = User.register("test", "test")
        self.token = jwt.encode(
            {
                "username": self.user.username,
                "exp": datetime.utcnow()
                + timedelta(minutes=config.JWT_EXPIRATION_MINUTES),
            },
            config.SECRET_KEY,
        )
        self.token = self.token.decode("UTF-8")

        self.admin_user = User.register("admin", "admin", True)
        self.admin_token = jwt.encode(
            {
                "username": self.admin_user.username,
                "exp": datetime.utcnow()
                + timedelta(minutes=config.JWT_EXPIRATION_MINUTES),
            },
            config.SECRET_KEY,
        )
        self.admin_token = self.admin_token.decode("UTF-8")
        ES.indices.create(index=config.ES_INDEX, body=movie_mapping())

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        ES.indices.delete(index=config.ES_INDEX)

    def test_add_movie(self):
        genres = ["Adventure", " Family", " Fantasy", " Musical"]
        for genre in genres:
            g = Genres(title=genre)
            g.save()

        response = self.client.post(
            "/api/v1/add_movie",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            data=json.dumps(
                {
                    "popularity": 83.0,
                    "director": "Victor Fleming",
                    "genre": [
                        "Adventure",
                        " Family",
                        " Fantasy",
                        " Musical"
                    ],
                    "imdb_score": 8.3,
                    "name": "The Wizard of Oz"
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(1, Movies.query.count())

    def test_add_movie_auth_fail(self):
        response = self.client.post(
            "/api/v1/add_movie",
            headers={"Authorization": f"Bearer {self.token}"},
            data=json.dumps(
                {
                    "popularity": 83.0,
                    "director": "Victor Fleming",
                    "genre": [
                        "Adventure",
                        " Family",
                        " Fantasy",
                        " Musical"
                    ],
                    "imdb_score": 8.3,
                    "name": "The Wizard of Oz"
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(401, response.status_code)

    def test_movie_already_exists(self):
        genres = ["Adventure", " Family", " Fantasy", " Musical"]
        genre_list = []
        for genre in genres:
            g = Genres(title=genre)
            g.save()
            genre_list.append(g)

        movie = Movies(name="The Wizard of Oz", director="Victor Fleming", imdb_score=8.3, popularity=83.0)
        movie.genres.extend(genre_list)
        movie.save()
        print(movie)

        response = self.client.post(
            "/api/v1/add_movie",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            data=json.dumps(
                {
                    "popularity": 83.0,
                    "director": "Victor Fleming",
                    "genre": [
                        "Adventure",
                        " Family",
                        " Fantasy",
                        " Musical"
                    ],
                    "imdb_score": 8.3,
                    "name": "The Wizard of Oz"
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(409, response.status_code)
        self.assertEqual({"message": "Movie already exists"}, json.loads(response.data.decode("UTF-8")))

    def test_genre_not_found(self):
        response = self.client.post(
            "/api/v1/add_movie",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            data=json.dumps(
                {
                    "popularity": 83.0,
                    "director": "Victor Fleming",
                    "genre": ["Adventure", " Fantasy", " Musical"],
                    "imdb_score": 8.3,
                    "name": "The Wizard of Oz"
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(404, response.status_code)
        self.assertEqual({"message": "Genre not found"}, json.loads(response.data.decode("UTF-8")))

    def test_movie_invalid_data(self):
        response = self.client.post(
            "/api/v1/add_movie",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            data=json.dumps(
                {
                    "popularity": 83.0,
                    "director": "Victor Fleming",
                    "genre": [
                        "Adventure",
                        " Family",
                        " Fantasy",
                        " Musical"
                    ],
                    "imdb_score": 8.3,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual({"message": "Missing data"}, json.loads(response.data.decode("UTF-8")))

    def test_search_movie(self):
        genres = ["Adventure", " Family", " Fantasy", " Musical"]
        genre_list = []
        for genre in genres:
            g = Genres(title=genre)
            g.save()
            genre_list.append(g)
        movie = Movies(name="The Wizard of Oz", director="Victor Fleming", imdb_score=8.3, popularity=83.0)
        movie.genres.extend(genre_list)
        movie.save()
        print(movie)

        response = self.client.get(
            "/api/v1/search_movie?name=wizard",
            headers={"Authorization": f"Bearer {self.token}"}
        )

        self.assertEqual(200, response.status_code)
        response_json = json.loads(response.data.decode("utf-8"))
        self.assertEqual(1, len(response_json["movies"]))

    def test_movie_not_found(self):
        response = self.client.get(
            "/api/v1/search_movie?name=wizard",
            headers={"Authorization": f"Bearer {self.token}"}
        )

        self.assertEqual(404, response.status_code)
        self.assertEqual({"message": "Movie not found"}, json.loads(response.data.decode("UTF-8")))
