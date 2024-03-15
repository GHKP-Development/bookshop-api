from time import sleep

from config import Config
from src.core.category import ProductCategory
from src.core.product import Product
from src.db.connection import Database
from src.utils.logging.logger import Logger


def main():
    cfg = Config.from_file()
    logger = Logger("MAIN", cfg.log_level)
    logger.info("Initializing database...")
    db = Database(cfg.database, logger.clone("DB"))
    product = Product(name="proba",
                      category=ProductCategory.ARTS,
                      price=1,
                      description="",
                      image_path="",
                      producer="",
                      characteristics={"1": 2},
                      quantity=1)
    if not db.insert_product(product):
        logger.error("Failed to insert product")
    else:
        logger.info(f"Product inserted with id: {product.id}")

    get_product = db.get_product(product_id=14)
    logger.info(f"Product extracted: {get_product}")

    product.name = "proba2"
    if not db.update_product(product):
        logger.error("Could not update product in main")
    else:
        logger.info(f"Updated {product}")
    sleep(1120)


if __name__ == "__main__":
    main()
