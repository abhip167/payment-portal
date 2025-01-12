from typing import Any

from pydantic_settings import BaseSettings
from pymongo import MongoClient

import os
from dotenv import load_dotenv
load_dotenv()

class Config(BaseSettings):
    CORS_ORIGINS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]
    CORS_METHODS: list[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

    MONGODATABASE: str = "payment_database"
    MONGO_URL: str = os.getenv("MONGODB_URI")


# environmental variables
env = Config()

# FastAPI configurations
fastapi_config: dict[str, Any] = {
    "title": "API",
}

mongo_url = ""

if env.MONGO_URL:
    mongo_url = env.MONGO_URL

# MongoDB connection
client = MongoClient(mongo_url)

# MongoDB database
database = client[env.MONGODATABASE]