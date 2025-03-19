import unittest
from contextlib import contextmanager
from unittest.mock import patch

from flask import Flask, template_rendered

from api import views


@contextmanager
def captured_templates(app):
    """Context manager to capture templates rendered during a request"""
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


class TestViews(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = Flask(__name__)
        cls.app.config["TESTING"] = True
        cls.app.secret_key = "test_secret_key"
        cls.app.register_blueprint(views.bp)

    def setUp(self):
        self.client = self.app.test_client()
        self.mock_user = {
            "user_id": "test123",
            "name": "Test User",
            "email": "test@example.com",
        }

    @patch("api.views.UserModel.scan")
    def test_index_success(self, mock_scan):
        mock_scan.return_value = [self.mock_user]

        with captured_templates(self.app) as templates:
            response = self.client.get("/")

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, "index.html")
            self.assertEqual(context["users"], [self.mock_user])

    @patch("api.views.UserModel.scan")
    def test_index_error(self, mock_scan):
        mock_scan.side_effect = Exception("Database error")

        with captured_templates(self.app) as templates:
            response = self.client.get("/")

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, "error.html")
            self.assertEqual(context["error"], "Database error")

    def test_new_user_get(self):
        with captured_templates(self.app) as templates:
            response = self.client.get("/users/new")

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, "new_user.html")

    @patch("api.views.UserModel.create")
    def test_new_user_post_success(self, mock_create):
        mock_create.return_value = self.mock_user

        response = self.client.post(
            "/users/new",
            data={
                "user_id": "test123",
                "name": "Test User",
                "email": "test@example.com",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        mock_create.assert_called_once_with(
            {"user_id": "test123", "name": "Test User", "email": "test@example.com"}
        )

    @patch("api.views.UserModel.create")
    def test_new_user_post_error(self, mock_create):
        mock_create.side_effect = Exception("Database error")

        with captured_templates(self.app) as templates:
            response = self.client.post(
                "/users/new",
                data={
                    "user_id": "test123",
                    "name": "Test User",
                    "email": "test@example.com",
                },
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, "new_user.html")
            self.assertEqual(context["error"], "Database error")

    @patch("api.views.UserModel.get")
    def test_view_user_success(self, mock_get):
        mock_get.return_value = self.mock_user

        with captured_templates(self.app) as templates:
            response = self.client.get("/users/test123")

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, "view_user.html")
            self.assertEqual(context["user"], self.mock_user)

    @patch("api.views.UserModel.get")
    def test_view_user_not_found(self, mock_get):
        mock_get.side_effect = Exception("DoesNotExist")

        with captured_templates(self.app) as templates:
            response = self.client.get("/users/nonexistent")

            self.assertEqual(response.status_code, 404)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, "error.html")
            self.assertEqual(context["error"], "User nonexistent not found")

    @patch("api.views.UserModel.get")
    def test_view_user_error(self, mock_get):
        mock_get.side_effect = Exception("Database error")

        with captured_templates(self.app) as templates:
            response = self.client.get("/users/test123")

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, "error.html")
            self.assertEqual(context["error"], "Database error")

    @patch("api.views.UserModel.delete")
    def test_delete_user_success(self, mock_delete):
        mock_delete.return_value = {}

        response = self.client.post("/users/test123/delete", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        mock_delete.assert_called_once_with("test123")

    @patch("api.views.UserModel.delete")
    def test_delete_user_error(self, mock_delete):
        mock_delete.side_effect = Exception("Database error")

        with captured_templates(self.app) as templates:
            response = self.client.post("/users/test123/delete")

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, "error.html")
            self.assertEqual(context["error"], "Database error")


class TestViewsIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = Flask(__name__)
        cls.app.config["TESTING"] = True
        cls.app.secret_key = "test_secret_key"
        cls.app.register_blueprint(views.bp)

    def setUp(self):
        self.client = self.app.test_client()

        self.patcher = patch("flask.templating._render")
        self.mock_render = self.patcher.start()
        self.mock_render.side_effect = lambda template, context, app: str(template)

        self.mock_user = {
            "user_id": "test123",
            "name": "Test User",
            "email": "test@example.com",
        }

    def tearDown(self):
        self.patcher.stop()

    @patch("api.views.UserModel.scan")
    def test_index_renders_with_users(self, mock_scan):
        mock_scan.return_value = [self.mock_user]

        response = self.client.get("/")

        mock_scan.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.mock_render.assert_called()

    @patch("api.views.UserModel.create")
    def test_new_user_redirects_on_success(self, mock_create):
        response = self.client.post(
            "/users/new",
            data={
                "user_id": "test123",
                "name": "Test User",
                "email": "test@example.com",
            },
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue("/" in response.location)

    @patch("api.views.UserModel.delete")
    def test_delete_redirects_on_success(self, mock_delete):
        response = self.client.post("/users/test123/delete", follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertTrue("/" in response.location)
