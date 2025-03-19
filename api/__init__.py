import logging
import os

from .dynamodb import create_tables, list_tables

logging_level = os.environ.get("LOGGING_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, logging_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

logger.info("Initializing DynamoDB tables...")
create_tables()

tables = list_tables()
logger.info(f"Existing tables: {tables}")
