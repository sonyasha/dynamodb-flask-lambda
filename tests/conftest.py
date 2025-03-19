# conftest.py

import os
from unittest.mock import MagicMock, patch

import pytest

from api.app import app as flask_app


@pytest.fixture(autouse=True, scope="session")
def setup_test_environment():
    os.environ["AWS_REGION"] = "us-east-1"
    os.environ["AWS_ACCESS_KEY_ID"] = "test-key"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test-secret"
    os.environ["DYNAMODB_HOST"] = "http://dynamodb:8000"
    yield


@pytest.fixture(scope="module")
def client():
    flask_app.config.update(
        {
            "TESTING": True,
        }
    )
    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            yield testing_client


@pytest.fixture
def setup_dynamodb_mock():
    with patch("api.dynamodb.dynamodb_client") as mock_client, patch(
        "api.dynamodb.dynamodb_resource"
    ) as mock_resource:

        mock_table = MagicMock()
        mock_resource.Table.return_value = mock_table

        yield mock_client, mock_resource, mock_table
