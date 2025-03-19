from unittest.mock import MagicMock

from botocore.exceptions import ClientError


class TestDynamoDBIntegration:

    def test_create_tables_already_exists(self, setup_dynamodb_mock):
        """Test table creation when table already exists"""
        mock_client, _, _ = setup_dynamodb_mock

        from api.dynamodb import create_tables

        create_tables()

        mock_client.describe_table.assert_called_once_with(TableName="UserTable")
        mock_client.create_table.assert_not_called()

    def test_create_tables_new(self, setup_dynamodb_mock):
        mock_client, _, _ = setup_dynamodb_mock
        mock_client.describe_table.side_effect = ClientError(
            {"Error": {"Code": "ResourceNotFoundException", "Message": "Not found"}},
            "operation",
        )
        mock_waiter = MagicMock()
        mock_client.get_waiter.return_value = mock_waiter

        from api.dynamodb import create_tables

        create_tables()

        mock_client.describe_table.assert_called_once_with(TableName="UserTable")
        mock_client.create_table.assert_called_once()
        mock_waiter.wait.assert_called_once_with(TableName="UserTable")

    def test_list_tables(self, setup_dynamodb_mock):
        mock_client, _, _ = setup_dynamodb_mock
        mock_client.list_tables.return_value = {"TableNames": ["UserTable"]}

        from api.dynamodb import list_tables

        result = list_tables()

        mock_client.list_tables.assert_called_once()
        assert result == ["UserTable"]

    def test_get_user_table(self, setup_dynamodb_mock):
        _, mock_resource, mock_table = setup_dynamodb_mock

        from api.dynamodb import get_user_table

        result = get_user_table()

        mock_resource.Table.assert_called_once_with("UserTable")
        assert result == mock_table
