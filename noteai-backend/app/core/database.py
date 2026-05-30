from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

_client: AsyncIOMotorClient = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGODB_URL)
    return _client


def get_db():
    return get_client()["noteai"]


# Collections — use these across the app
def get_users_collection():
    return get_db()["users"]


def get_notes_collection():
    return get_db()["notes"]


async def create_indexes():
    """Create MongoDB indexes on startup."""
    users = get_users_collection()
    notes = get_notes_collection()

    # Unique email index
    await users.create_index("email", unique=True)

    # Notes: text index for full-text search
    await notes.create_index([("title", "text"), ("content", "text")])

    # Notes: compound index for user queries
    await notes.create_index([("user_id", 1), ("updated_at", -1)])

    print("✅ MongoDB indexes created")


async def close_connection():
    global _client
    if _client:
        _client.close()
        _client = None
