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
                      category=ProductCategory.ARTS.value,
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

    # extracted_product = db.get_product(product_id=product.id)
    # logger.info(f"Product extracted: {extracted_product}")
    #
    # extracted_product.name = "proba4"
    # if not db.update_product(extracted_product):
    #     logger.error("Could not update product in main")
    # else:
    #     logger.info(f"Updated {extracted_product}")
    db.delete_product(product_id=99)


if __name__ == "__main__":
    main()
