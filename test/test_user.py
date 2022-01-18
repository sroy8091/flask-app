import json
import unittest
import jwt

import config
from models import User
from models.abc import db
from server import server


class TestUser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = server.test_client()

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_register(self):
        response = self.client.post(
            "/api/v1/register",
            content_type="application/json",
            data=json.dumps({"username": "test", "password": "test"}),
        )

        self.assertEqual(201, response.status_code)
        response_json = json.loads(response.data.decode("utf-8"))
        self.assertEqual({"message": "Registration successful."}, response_json)
        self.assertEqual(1, User.query.count())

    def test_register_admin(self):
        response = self.client.post(
            "/api/v1/register",
            content_type="application/json",
            data=json.dumps({"username": "test", "password": "test", "is_admin": True}),
        )

        self.assertEqual(201, response.status_code)
        response_json = json.loads(response.data.decode("utf-8"))
        self.assertEqual({"message": "Registration successful."}, response_json)
        self.assertEqual(1, User.query.filter_by(is_admin=True).count())

    def test_register_fail(self):
        user = User.register("test", "test")
        response = self.client.post(
            "/api/v1/register",
            content_type="application/json",
            data=json.dumps({"username": "test", "password": "test"}),
        )

        self.assertEqual(400, response.status_code)
        response_json = json.loads(response.data.decode("utf-8"))
        self.assertEqual({"message": "Invalid username or password."}, response_json)

    def test_login(self):
        user = User.register("test", "test")

        response = self.client.post(
            "/api/v1/login",
            content_type="application/json",
            data=json.dumps({"username": "test", "password": "test"}),
        )

        self.assertEqual(200, response.status_code)
        response_json = json.loads(response.data.decode("utf-8"))
        data = jwt.decode(response_json['token'], config.SECRET_KEY)
        self.assertEqual(user, User.query.filter_by(username=data["username"]).first())

    def test_login_fail(self):
        response = self.client.post(
            "/api/v1/login",
            content_type="application/json",
            data=json.dumps({"username": "test", "password": "test"}),
        )

        self.assertEqual(401, response.status_code)
        response_json = json.loads(response.data.decode("utf-8"))
        self.assertEqual({"message": "Invalid username or password."}, response_json)

    def test_missing_token(self):
        response = self.client.get(
            "/api/v1/user_details"
        )

        self.assertEqual(401, response.status_code)
        response_json = json.loads(response.data.decode("utf-8"))
        self.assertEqual({"message": "Token is missing"}, response_json)

    def test_invalid_token(self):
        response = self.client.get(
            "/api/v1/user_details",
            headers={'Authorization': 'Bearer invalid_token'}
        )

        self.assertEqual(403, response.status_code)
        response_json = json.loads(response.data.decode("utf-8"))
        self.assertEqual({"message": "Invalid token"}, response_json)
