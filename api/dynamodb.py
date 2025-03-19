import logging
import os

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TABLE_NAME = "UserTable"


dynamodb_client = boto3.client(
    "dynamodb",
    endpoint_url=os.environ.get("DYNAMODB_HOST", None),
    region_name=os.environ["AWS_REGION"],
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
)

dynamodb_resource = boto3.resource(
    "dynamodb",
    endpoint_url=os.environ.get("DYNAMODB_HOST", None),
    region_name=os.environ["AWS_REGION"],
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
)


def create_user_table():

    try:
        dynamodb_client.describe_table(TableName=TABLE_NAME)
        logger.info(f"Table {TABLE_NAME} already exists")
        return
    except ClientError as e:
        if e.response["Error"]["Code"] != "ResourceNotFoundException":
            logger.error(f"Error checking table existence: {e}")
            raise

    logger.info(f"Creating table {TABLE_NAME}...")

    try:
        dynamodb_client.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {"AttributeName": "user_id", "KeyType": "HASH"}  # Partition key
            ],
            AttributeDefinitions=[
                {"AttributeName": "user_id", "AttributeType": "S"}  # String
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        waiter = dynamodb_client.get_waiter("table_exists")
        waiter.wait(TableName=TABLE_NAME)

        logger.info(f"Table {TABLE_NAME} created successfully")
    except ClientError as e:
        logger.error(f"Error creating table: {e}")
        raise


def list_tables():
    try:
        response = dynamodb_client.list_tables()
        return response["TableNames"]
    except ClientError as e:
        logger.error(f"Error listing tables: {e}")
        raise


def get_user_table():
    return dynamodb_resource.Table(TABLE_NAME)


def create_tables():
    create_user_table()
    logger.info("All tables created successfully")
