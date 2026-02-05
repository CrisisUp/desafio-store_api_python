from pydantic import ValidationError
import pytest
from store.schemas.product import ProductIn
from tests.factories import product_data


def test_schemas_return_success():
    data = product_data()
    product = ProductIn.model_validate(data)
    assert product.name == "Iphone 14 Pro Max"


def test_schemas_return_raise():
    # Dado que falta o campo "status"
    data = {"name": "Iphone 14 Pro Max", "quantity": 10, "price": 8.500}

    with pytest.raises(ValidationError) as err:
        ProductIn.model_validate(data)

    # Pegamos apenas o primeiro erro da lista
    error = err.value.errors()[0]

    # Validamos o que realmente importa para a lógica de negócio
    assert error["type"] == "missing"
    assert error["loc"] == ("status",)
    assert error["msg"] == "Field required"
