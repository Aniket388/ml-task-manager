import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "ml_task_manager")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]


async def get_database():
    return db
