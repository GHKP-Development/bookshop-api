from time import sleep

from config import Config
from src.core.category import ProductCategory
from src.core.product import Product
from src.db.connection import Database
from src.utils.logging.logger import Logger
from src.web.server import Application


def main():
    cfg = Config.from_file()
    logger = Logger.from_config("MAIN", cfg.logging)
    logger.info("Initializing database...")
    database = Database(cfg.database, logger.clone("DB"))

    product = Product(
        name="name name name",
        category=ProductCategory.TOYS,
        price=12.99,
        description="empty description",
        image_path="some/path/",
        quantity=1,
        producer="Versace  versace",
        characteristics={"tmp": "tmp"}
    )
    database.insert_product(product)
    logger.debug(f"Inserted product with id: {product.id}")

    server = Application(port=80, database=database, logger=logger.clone("WEB"))
    server.run()

    server.search_products(name="proba")
    server.get_product(product_id=26)


if __name__ == "__main__":
    main()
