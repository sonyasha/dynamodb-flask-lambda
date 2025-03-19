from botocore.exceptions import ClientError

from .dynamodb import get_user_table


class UserModel:
    @staticmethod
    def get(user_id):
        """Get a user by user_id"""
        table = get_user_table()
        try:
            response = table.get_item(Key={"user_id": user_id})
            if "Item" not in response:
                raise Exception("DoesNotExist")
            return response["Item"]
        except ClientError as e:
            print(f"Error getting user: {e}")
            raise

    @staticmethod
    def create(user_data):
        """Create a new user"""
        table = get_user_table()
        try:
            table.put_item(Item=user_data)
            return user_data
        except ClientError as e:
            print(f"Error creating user: {e}")
            raise

    @staticmethod
    def scan():
        """Scan all users"""
        table = get_user_table()
        try:
            response = table.scan()
            return response.get("Items", [])
        except ClientError as e:
            print(f"Error scanning users: {e}")
            raise

    @staticmethod
    def delete(user_id):
        """Delete a user"""
        table = get_user_table()
        try:
            response = table.delete_item(Key={"user_id": user_id})
            return response
        except ClientError as e:
            print(f"Error deleting user: {e}")
            raise
