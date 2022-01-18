"""
Define the User model
"""
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from . import db
from .abc import BaseModel, MetaBaseModel


class User(db.Model, BaseModel, UserMixin, metaclass=MetaBaseModel):
    """ The User model """

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, username, password=None, is_admin=False):
        """ Create a new User """
        self.username = username
        self.password = password
        self.is_admin = is_admin

    def set_password(self, password):
        """Set user password hash."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Verify user's password."""
        return check_password_hash(self.password, password)

    @staticmethod
    def register(username, password, is_admin=False):
        """Register a user."""
        prev_user = User.query.filter_by(username=username, is_active=True).first()
        if username and password and not prev_user:
            user = User(username=username, is_admin=is_admin)
            user.set_password(password)
            user.save()
            return user
        return None

    @staticmethod
    def get_user(username, password):
        """Find and authenticate a user."""
        user = User.query.filter_by(username=username, is_active=True).first()
        if user and password and user.check_password(password):
            return user
        return None
