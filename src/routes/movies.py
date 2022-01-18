from flask import Blueprint, jsonify, request

from models import Genres, Movies, db
from util.elastic_utils import fuzzy_search
from util.permission import token_required

movies_bp = Blueprint("movies", __name__)


@movies_bp.route("/add_movie", methods=["POST"], strict_slashes=False)
@token_required
def add_movie(current_user):
    """
    Add a movie to the database
    """
    try:
        # Get the movie title and the user id
        data = request.get_json()
        name = data["name"]
        director = data["director"]
        imdb_score = data["imdb_score"]
        popularity = data["popularity"]
        genre = data["genre"]

        # Add the movie to the database

        if not current_user.is_admin:
            return jsonify({"message": "You are not authorized to add a movie"}), 401

        if Movies.query.filter_by(name=name).first():
            return jsonify({"message": "Movie already exists"}), 409

        movie = Movies(
            name=name, director=director, imdb_score=imdb_score, popularity=popularity
        )
        genre_ins = Genres.query.filter(Genres.title.in_(genre)).all()
        if len(genre_ins) != len(genre):
            return jsonify({"message": "Genre not found"}), 404
        movie.genres.extend(genre_ins)
        movie.save()
        return jsonify({"message": "Movie added successfully"}), 201
    except KeyError:
        return jsonify({"message": "Missing data"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Something went wrong", "error": str(e)}), 500


@movies_bp.route("/search_movie", methods=["GET"], strict_slashes=False)
@token_required
def search_movie(current_user):
    """
    Search for a movie in the database
    """
    # Get the movie title and the user id
    name = request.args.get("name")

    # Search for the movie in the database
    try:
        movies = Movies.format_search(fuzzy_search(name, ["name", "director"]))
        print(movies)
        if len(movies) == 0:
            return jsonify({"message": "Movie not found"}), 404
        return (
            jsonify({"message": "Movie found", "movies": movies}),
            200,
        )
    except Exception as e:
        print(e)
        return jsonify({"message": "Something went wrong", "error": str(e)}), 500
