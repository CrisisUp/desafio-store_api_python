from typing import List
from uuid import UUID
from decimal import Decimal
from bson import Decimal128
from datetime import datetime, UTC
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import pymongo
from store.db.mongo import db_client
from store.models.product import ProductModel
from store.schemas.product import ProductIn, ProductOut, ProductUpdate, ProductUpdateOut
from store.core.exceptions import CollisionException, NotFoundException


class ProductUsecase:
    def __init__(self) -> None:
        self.client: AsyncIOMotorClient = db_client.get()
        self.database: AsyncIOMotorDatabase = self.client.get_database()
        self.collection = self.database.get_collection("products")

    async def create(self, body: ProductIn) -> ProductOut:
        existing_product = await self.collection.find_one({"name": body.name})
        if existing_product:
            raise CollisionException(message=f"Product with name {body.name} already exists")

        product_model = ProductModel(**body.model_dump())
        data = product_model.model_dump()
        data["price"] = Decimal128(str(data["price"]))
        
        await self.collection.insert_one(data)
        return ProductOut(**product_model.model_dump())

    async def get(self, id: UUID) -> ProductOut:
        result = await self.collection.find_one({"id": id, "is_active": True})
        if not result:
            raise NotFoundException(message=f"Product not found with filter: {id}")
        return ProductOut(**result)

    async def query(
        self, min_price: float = None, max_price: float = None
    ) -> List[ProductOut]:
        filters = {"is_active": True}

        if min_price or max_price:
            filters["price"] = {}
            if min_price:
                filters["price"]["$gte"] = Decimal128(str(min_price))
            if max_price:
                filters["price"]["$lte"] = Decimal128(str(max_price))

        return [ProductOut(**item) async for item in self.collection.find(filters)]

    async def update(self, id: UUID, body: ProductUpdate) -> ProductUpdateOut:
        update_data = body.model_dump(exclude_none=True)

        if update_data:
            update_data["updated_at"] = datetime.now(UTC)

        if "price" in update_data:
            update_data["price"] = Decimal128(str(update_data["price"]))

        result = await self.collection.find_one_and_update(
            filter={"id": id},
            update={"$set": update_data},
            return_document=pymongo.ReturnDocument.AFTER,
        )

        if not result:
            raise NotFoundException(message=f"Product not found with filter: {id}")
        return ProductUpdateOut(**result)

    async def delete(self, id: UUID) -> bool:
        result = await self.collection.find_one_and_update(
            filter={"id": id, "is_active": True},
            update={"$set": {"is_active": False, "updated_at": datetime.now(UTC)}},
            return_document=pymongo.ReturnDocument.AFTER,
        )
        if not result:
            raise NotFoundException(message=f"Product not found with filter: {id}")
        
        return True

product_usecase = ProductUsecase()
