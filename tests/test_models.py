import unittest
from unittest.mock import MagicMock, patch

from botocore.exceptions import ClientError

from api.models import UserModel


class TestUserModel(unittest.TestCase):
    def setUp(self):
        self.mock_user = {
            "user_id": "test123",
            "name": "Test User",
            "email": "test@example.com",
        }
        self.mock_table = MagicMock()

    @patch("api.models.get_user_table")
    def test_get_user_success(self, mock_get_table):
        mock_get_table.return_value = self.mock_table
        self.mock_table.get_item.return_value = {"Item": self.mock_user}

        result = UserModel.get("test123")

        self.mock_table.get_item.assert_called_once_with(Key={"user_id": "test123"})
        self.assertEqual(result, self.mock_user)

    @patch("api.models.get_user_table")
    def test_get_user_not_found(self, mock_get_table):
        mock_get_table.return_value = self.mock_table
        self.mock_table.get_item.return_value = {}

        with self.assertRaises(Exception) as context:
            UserModel.get("nonexistent")

        self.assertEqual(str(context.exception), "DoesNotExist")

    @patch("api.models.get_user_table")
    def test_get_user_client_error(self, mock_get_table):
        mock_get_table.return_value = self.mock_table
        self.mock_table.get_item.side_effect = ClientError(
            {"Error": {"Code": "InternalServerError", "Message": "Test error"}},
            "operation",
        )

        with self.assertRaises(ClientError):
            UserModel.get("test123")

    @patch("api.models.get_user_table")
    def test_create_user_success(self, mock_get_table):
        mock_get_table.return_value = self.mock_table

        result = UserModel.create(self.mock_user)

        self.mock_table.put_item.assert_called_once_with(Item=self.mock_user)
        self.assertEqual(result, self.mock_user)

    @patch("api.models.get_user_table")
    def test_create_user_client_error(self, mock_get_table):
        mock_get_table.return_value = self.mock_table
        self.mock_table.put_item.side_effect = ClientError(
            {"Error": {"Code": "InternalServerError", "Message": "Test error"}},
            "operation",
        )

        with self.assertRaises(ClientError):
            UserModel.create(self.mock_user)

    @patch("api.models.get_user_table")
    def test_scan_users_success(self, mock_get_table):
        mock_get_table.return_value = self.mock_table
        self.mock_table.scan.return_value = {"Items": [self.mock_user]}

        result = UserModel.scan()

        self.mock_table.scan.assert_called_once()
        self.assertEqual(result, [self.mock_user])

    @patch("api.models.get_user_table")
    def test_scan_users_empty(self, mock_get_table):
        mock_get_table.return_value = self.mock_table
        self.mock_table.scan.return_value = {}

        result = UserModel.scan()

        self.assertEqual(result, [])

    @patch("api.models.get_user_table")
    def test_scan_users_client_error(self, mock_get_table):
        mock_get_table.return_value = self.mock_table
        self.mock_table.scan.side_effect = ClientError(
            {"Error": {"Code": "InternalServerError", "Message": "Test error"}},
            "operation",
        )

        with self.assertRaises(ClientError):
            UserModel.scan()

    @patch("api.models.get_user_table")
    def test_delete_user_success(self, mock_get_table):
        mock_get_table.return_value = self.mock_table
        self.mock_table.delete_item.return_value = {}

        result = UserModel.delete("test123")

        self.mock_table.delete_item.assert_called_once_with(Key={"user_id": "test123"})
        self.assertEqual(result, {})

    @patch("api.models.get_user_table")
    def test_delete_user_client_error(self, mock_get_table):
        mock_get_table.return_value = self.mock_table
        self.mock_table.delete_item.side_effect = ClientError(
            {"Error": {"Code": "InternalServerError", "Message": "Test error"}},
            "operation",
        )

        with self.assertRaises(ClientError):
            UserModel.delete("test123")
