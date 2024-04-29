import dataclasses
from typing import Any

from src.db.models import ProductModel
from src.utils.types import nullable


@dataclasses.dataclass(repr=True)
class Product:
    name: str
    category: int
    price: float
    description: str
    image_paths: list[str]
    producer: str
    characteristics: dict[str, Any]
    quantity: int
    id: nullable(int) = None

    def to_db_model(self) -> ProductModel:
        return ProductModel(
            id=self.id,
            name=self.name,
            category=self.category,
            price=self.price,
            description=self.description,
            image_paths=";".join(self.image_paths),
            producer=self.producer,
            characteristics=self.characteristics,
            quantity=self.quantity
        )

    @classmethod
    def from_db_model(cls, db_model: ProductModel) -> 'Product':
        return cls(
            id=db_model.id,
            name=db_model.name,
            category=db_model.category,
            price=db_model.price,
            description=db_model.description,
            image_paths=db_model.image_path.split(";"),
            producer=db_model.producer,
            characteristics=db_model.characteristics,
            quantity=db_model.quantity
        )

    @classmethod
    def from_dict(cls, request_model: dict) -> 'Product':
        return cls(
            id=request_model.get("id"),
            name=request_model.get("name"),
            category=request_model.get("category"),
            price=request_model.get("price"),
            description=request_model.get("description"),
            image_paths=request_model.get("image_paths"),
            producer=request_model.get("producer"),
            characteristics=request_model.get("characteristics"),
            quantity=request_model.get("quantity")
        )