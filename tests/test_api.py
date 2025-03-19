import json
import unittest
from unittest.mock import patch

from api.app import app


class TestHealthCheckEndpoint:
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == {"status": "healthy"}


class TestUserEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.mock_user = {
            "user_id": "test123",
            "name": "Test User",
            "email": "test@example.com",
        }

    @patch("api.models.UserModel.create")
    def test_create_user_success(self, mock_create):
        """Test creating a user successfully"""
        mock_create.return_value = self.mock_user
        response = self.app.post(
            "/users", data=json.dumps(self.mock_user), content_type="application/json"
        )

        mock_create.assert_called_once_with(self.mock_user)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "User created")
        self.assertEqual(data["user_id"], "test123")

    @patch("api.models.UserModel.create")
    def test_create_user_failure(self, mock_create):
        """Test handling errors when creating a user"""
        mock_create.side_effect = Exception("Database error")
        response = self.app.post(
            "/users", data=json.dumps(self.mock_user), content_type="application/json"
        )

        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Database error")

    @patch("api.models.UserModel.scan")
    def test_list_users_success(self, mock_scan):
        """Test listing all users successfully"""
        mock_scan.return_value = [self.mock_user]
        response = self.app.get("/users")

        mock_scan.assert_called_once()
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, [self.mock_user])

    @patch("api.models.UserModel.scan")
    def test_list_users_empty(self, mock_scan):
        """Test listing users when no users exist"""
        mock_scan.return_value = []
        response = self.app.get("/users")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, [])

    @patch("api.models.UserModel.scan")
    def test_list_users_error(self, mock_scan):
        """Test handling errors when listing users"""
        mock_scan.side_effect = Exception("Database error")
        response = self.app.get("/users")

        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Database error")

    @patch("api.models.UserModel.delete")
    def test_delete_user_success(self, mock_delete):
        """Test deleting a user successfully"""
        mock_delete.return_value = {}
        response = self.app.delete("/users/test123")

        mock_delete.assert_called_once_with("test123")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "User deleted")

    @patch("api.models.UserModel.delete")
    def test_delete_user_error(self, mock_delete):
        """Test handling errors when deleting a user"""
        mock_delete.side_effect = Exception("Database error")
        response = self.app.delete("/users/test123")

        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Database error")
