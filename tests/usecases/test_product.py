import asyncio
from typing import List
from uuid import UUID
import pytest
from store.core.exceptions import CollisionException, NotFoundException
from store.schemas.product import ProductIn, ProductOut, ProductUpdate, ProductUpdateOut
from store.usecases.product import product_usecase


async def test_usecases_create_should_return_success(product_in):
    result = await product_usecase.create(body=product_in)
    assert isinstance(result, ProductOut)
    assert result.name == "Iphone 14 Pro Max"


async def test_usecases_get_should_return_success(product_inserted):
    result = await product_usecase.get(id=product_inserted.id)
    assert isinstance(result, ProductOut)
    assert result.name == "Iphone 14 Pro Max"


async def test_usecases_get_should_not_found():
    with pytest.raises(NotFoundException) as err:
        await product_usecase.get(id=UUID("1e4f214e-85f7-461a-89d0-a751a32e3bb9"))

    assert (
        err.value.message
        == "Product not found with filter: 1e4f214e-85f7-461a-89d0-a751a32e3bb9"
    )


@pytest.mark.usefixtures("products_inserted")
async def test_usecases_query_should_return_success():
    result = await product_usecase.query()
    assert isinstance(result, List)
    assert len(result) > 1


async def test_usecases_update_should_return_success(product_up, product_inserted):
    product_up.price = "7.500"
    result = await product_usecase.update(id=product_inserted.id, body=product_up)
    assert isinstance(result, ProductUpdateOut)


async def test_usecases_delete_should_return_success(product_inserted):
    result = await product_usecase.delete(id=product_inserted.id)
    assert result is True


async def test_usecases_delete_should_not_found():
    with pytest.raises(NotFoundException) as err:
        await product_usecase.delete(id=UUID("1e4f214e-85f7-461a-89d0-a751a32e3bb9"))

    assert (
        err.value.message
        == "Product not found with filter: 1e4f214e-85f7-461a-89d0-a751a32e3bb9"
    )


async def test_usecases_update_should_update_updated_at(product_inserted):
    original_updated_at = product_inserted.updated_at
    await asyncio.sleep(0.01)
    update_body = ProductUpdate(quantity=50)
    result = await product_usecase.update(id=product_inserted.id, body=update_body)
    assert result.updated_at > original_updated_at


async def test_usecases_create_should_return_collision(product_in):
    await product_usecase.create(body=product_in)
    with pytest.raises(CollisionException) as err:
        await product_usecase.create(body=product_in)
    assert err.value.message == f"Product with name {product_in.name} already exists"


async def test_usecases_delete_should_soft_delete(product_inserted):
    await product_usecase.delete(id=product_inserted.id)
    with pytest.raises(NotFoundException):
        await product_usecase.get(id=product_inserted.id)
    raw_data = await product_usecase.collection.find_one({"id": product_inserted.id})
    assert raw_data["is_active"] is False