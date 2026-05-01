import databases
import sqlalchemy
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as aioredis
from app.core.config import POSTGRES_URL, POSTGRES_URL_SYNC, MONGO_URL, MONGO_DB, REDIS_URL

# PostgreSQL
database = databases.Database(POSTGRES_URL)
metadata = sqlalchemy.MetaData()
engine   = sqlalchemy.create_engine(POSTGRES_URL_SYNC)

# MongoDB
mongo_client = AsyncIOMotorClient(MONGO_URL)
mongo_db     = mongo_client[MONGO_DB]

# Redis
redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)