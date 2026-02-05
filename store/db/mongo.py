from motor.motor_asyncio import AsyncIOMotorClient

# Importamos a representação padrão de UUID
from bson.binary import UuidRepresentation
from store.core.config import settings


class MongoClient:
    def __init__(self) -> None:
        self.client: AsyncIOMotorClient = AsyncIOMotorClient(
            settings.DATABASE_URL, uuidRepresentation="standard"
        )

    def get(self) -> AsyncIOMotorClient:
        return self.client


db_client = MongoClient()
