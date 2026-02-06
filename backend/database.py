import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

client = AsyncIOMotorClient(MONGODB_URI)
database = client.get_database()

# Collections
users_collection = database.get_collection("users")
accounts_collection = database.get_collection("accounts")
transactions_collection = database.get_collection("transactions")
bills_collection = database.get_collection("bills")


async def init_db():
    """Initialize database indexes"""
    await users_collection.create_index("email", unique=True)
    await accounts_collection.create_index("account_number", unique=True)
    await accounts_collection.create_index("user_id")
    await transactions_collection.create_index("account_id")
    await transactions_collection.create_index("created_at")
    await bills_collection.create_index("user_id")
