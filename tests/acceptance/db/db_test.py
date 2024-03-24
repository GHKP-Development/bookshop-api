import logging
import unittest
from decimal import Decimal

from config import DBConfig, DBEngineType
from src.core.category import ProductCategory
from src.core.product import Product
from src.db.connection import Database
from src.utils.logging.logger import Logger


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.logger = Logger(name="TEST", level=logging.DEBUG)
        self.db = Database(cfg=DBConfig(db_name="bookshop_tests", engine=DBEngineType.SQLITE), logger=self.logger)

    def test_crud_products(self):
        """
        1. insert
        2. get na tozi insert
        3. update
        4. delete
        """
        test_product = Product(
            name="test product",
            category=ProductCategory.ARTS,
            price=10.0,
            description="test description",
            image_path="test path",
            producer="test produces",
            characteristics={'1': 'sample'},
            quantity=5
        )
        self.assertTrue(self.db.insert_product(test_product))  # insert
        self.assertEqual(test_product, self.db.get_product(product_id=test_product.id))  # get
        test_product.name = "updated name"
        test_product.quantity = 5
        self.assertTrue(self.db.update_product(product=test_product))  # update
        self.assertEqual(test_product, self.db.get_product(product_id=test_product.id))
        self.assertTrue(self.db.delete_product(product_id=test_product.id))  # delete
        self.assertIsNone(self.db.get_product(product_id=test_product.id))
        self.assertFalse(self.db.delete_product(product_id=test_product.id))

    def test_search_products(self):
        test_product_1 = Product(
            name="test product 1",
            category=ProductCategory.ARTS,
            price=10.0,
            description="test description 1",
            image_path="test path",
            producer="test producer 1",
            characteristics={'1': 'sample 1'},
            quantity=5
        )
        test_product_2 = Product(
            name="test product 2",
            category=ProductCategory.TOYS,
            price=20.0,
            description="test description 2",
            image_path="test path",
            producer="test producer 2",
            characteristics={'2': 'sample 2'},
            quantity=5
        )
        test_product_3 = Product(
            name="test product 3",
            category=ProductCategory.CASES | ProductCategory.TOYS,
            price=30.0,
            description="test description 3",
            image_path="test path",
            producer="test producer 3",
            characteristics={'3': 'sample 3'},
            quantity=5
        )
        for product in (test_product_1, test_product_2, test_product_3):
            self.assertTrue(self.db.insert_product(product))

        results_by_name = self.db.search_products(name="test product 3")
        self.assertEqual(1, len(results_by_name))
        self.assertEqual(test_product_3, results_by_name[0])

        results_by_category = self.db.search_products(category=ProductCategory.TOYS)
        self.assertListEqual([test_product_2, test_product_3], results_by_category)

        results_by_min_price = self.db.search_products(min_price=Decimal.from_float(15.0))
        self.assertListEqual([test_product_2, test_product_3], results_by_min_price)

        results_by_max_price = self.db.search_products(max_price=Decimal.from_float(25.0))
        self.assertListEqual([test_product_1, test_product_2], results_by_max_price)

        results_by_producer = self.db.search_products(producer="test producer 1")
        self.assertEqual(test_product_1, results_by_producer[0])

    def tearDown(self):
        self.db.delete_all_products()
        # delete_sqlite_file(self.db.name + ".db")

