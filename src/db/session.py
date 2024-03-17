from sqlalchemy.orm import Session as SQLAlchemySession

from src.core.product import Product
from src.utils.logging.logger import Logger
from src.db.models import Base, ProductModel
from src.utils.types import nullable


class Session:

    def __init__(self, session: SQLAlchemySession, logger: Logger):
        self._logger: Logger = logger
        self._session: SQLAlchemySession = session

    def _insert(self, what: Base) -> int:
        """
        Insert a model into the database. We flush changes immediately so we can take the ID before committing session
        """
        self._session.add(what)
        self._session.flush()
        self._logger.debug(f"Inserted {what.__class__.__name__} with ID: {what.id}")
        return what.id

    def get_product(self, product_id: int) -> ProductModel | None:
        return self._session.query(ProductModel).filter_by(id=product_id).first()

    def search_products(self, **filters):
        query = self._session.query(ProductModel).filter_by(**filters)
        products = query.all()
        return products

    def insert_product(self, product: ProductModel):
        product_id = self._insert(product)
        self._logger.debug(f"Product {product.name} inserted with id {product_id}")

    def delete_product(self, product_id: int):
        if product := self._session.query(ProductModel).filter_by(id=product_id).first():
            self._session.delete(product)
            self._session.commit()

    def update_product(self, existing_product: ProductModel, product: Product) -> bool:
        existing_product.name = product.name
        existing_product.category = product.category
        existing_product.price = product.price
        existing_product.description = product.description
        existing_product.image_path = product.image_path
        existing_product.producer = product.producer
        existing_product.characteristics = product.characteristics
        existing_product.quantity = product.quantity
        self._session.commit()
        return True

