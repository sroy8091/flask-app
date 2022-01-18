from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested

from models import Genres, Movies


class GenreSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Genres
        load_instance = True
        include_relationships = True


class MoviesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Movies
        include_relationships = True
        load_instance = True

    genres = Nested(GenreSchema, many=True, exclude=("movies", "id"))
