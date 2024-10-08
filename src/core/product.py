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
    image_path: str
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
            image_path=self.image_path,
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
            image_path=db_model.image_path,
            producer=db_model.producer,
            characteristics=db_model.characteristics,
            quantity=db_model.quantity
        )
