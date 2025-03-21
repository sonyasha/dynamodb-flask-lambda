from botocore.exceptions import ClientError

from .dynamodb import get_user_table


class UserModel:
    @staticmethod
    def get(user_id):
        table = get_user_table()
        try:
            response = table.get_item(Key={"user_id": user_id})
            if "Item" not in response:
                raise Exception("DoesNotExist")
            return response["Item"]
        except ClientError:
            raise

    @staticmethod
    def create(user_data):
        table = get_user_table()
        try:
            table.put_item(Item=user_data)
            return user_data
        except ClientError:
            raise

    @staticmethod
    def scan():
        table = get_user_table()
        try:
            response = table.scan()
            return response.get("Items", [])
        except ClientError:
            raise

    @staticmethod
    def delete(user_id):
        table = get_user_table()
        try:
            response = table.delete_item(Key={"user_id": user_id})
            return response
        except ClientError:
            raise
