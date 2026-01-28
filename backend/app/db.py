from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from .config import Config


_client = None


def get_client():
    global _client
    if _client is None:
        _client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=2000)
    return _client


def get_db():
    client = get_client()
    try:
        client.server_info()
    except ServerSelectionTimeoutError as exc:
        raise RuntimeError("MongoDB not available") from exc
    return client[Config.DB_NAME]

