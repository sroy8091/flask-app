"""
Define the Movie model
"""
import config
from . import ES, db
from .abc import BaseModel, MetaBaseModel


class Movies(db.Model, BaseModel, metaclass=MetaBaseModel):
    __tablename__ = "movies"
    to_json_filter = ("genres",)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    imdb_score = db.Column(db.Float, nullable=False)
    director = db.Column(db.String(128), nullable=False)
    popularity = db.Column(db.Float, nullable=False)
    genres = db.relationship("Genres", secondary="movie_genre")

    def __init__(self, name, imdb_score, director, popularity):
        self.name = name
        self.imdb_score = imdb_score
        self.director = director
        self.popularity = popularity

    def save(self):
        db.session.add(self)
        db.session.commit()
        from models.schema import MoviesSchema

        try:
            ES.index(
                index=config.ES_INDEX,
                doc_type=config.ES_DOC_TYPE,
                id=self.id,
                body=MoviesSchema().dump(self),
                refresh=True
            )
        except Exception:
            raise Exception("Error indexing movie")
        return self

    @staticmethod
    def format_search(results):
        movies = [result["_source"] for result in results["hits"]["hits"]]
        for movie in movies:
            movie.pop('id')

        return movies


class Genres(db.Model, BaseModel, metaclass=MetaBaseModel):
    __tablename__ = "genres"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(128), nullable=False)
    movies = db.relationship("Movies", secondary="movie_genre")


class MovieGenre(db.Model, BaseModel, metaclass=MetaBaseModel):
    __tablename__ = "movie_genre"

    movie_id = db.Column(db.Integer, db.ForeignKey("movies.id"), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey("genres.id"), primary_key=True)
