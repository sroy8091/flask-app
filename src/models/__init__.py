from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from elasticsearch import Elasticsearch, RequestsHttpConnection

import config

db = SQLAlchemy()
ES = Elasticsearch(
    hosts=[{"host": config.ELASTICSEARCH['host'], "port": config.ELASTICSEARCH['port']}],
    connection_class=RequestsHttpConnection,
    max_retries=30,
    retry_on_timeout=True,
    request_timeout=30,
)

login_manager = LoginManager()

from .user import User
from .movies import Movies, Genres, MovieGenre
