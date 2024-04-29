import csv
import zipfile

from src.blob_storage.controller import BlobStorage
from src.core.category import ProductCategory
from src.core.product import Product


class UploadParser:
    def __init__(self, zip_file: zipfile.ZipFile, blob_storage: BlobStorage):
        self.zip_file: zipfile.ZipFile = zip_file
        self.products_to_create: list[Product] = []
        self.products_to_update: list[Product] = []
        self.products_to_delete: list[int] = []
        self.field_mapping: dict[str, int] = {}
        self.blob_storage: BlobStorage = blob_storage

    def parse(self):
        with self.zip_file.open("manifest.csv") as csv_file:
            reader = csv.reader(csv_file)
            header = next(reader)
            self.map_csv_headers(header)
            for row_number, row in enumerate(reader):
                match row[self.field_mapping["action"]]:
                    case "C":
                        product = self.create_product_from_row(row)
                        self.products_to_create.append(product)
                    case "U":
                        pass
                    case "D":
                        if not self.field_mapping.get("id"):
                            raise ValueError(f"No id provided for product on line {row_number + 2}")
                        self.products_to_delete.append(self.field_mapping["id"])

    @staticmethod
    def parse_categories(categories: str):
        split_categories = categories.split(";")

        sum_ = 0
        for category in split_categories:
            sum_ += ProductCategory.lookup(category)

        return sum_

    def map_csv_headers(self, header: list[str]):
        for index, column in enumerate(header):
            self.field_mapping[column.casefold()] = index

    def parse_images(self, image_names: str, product_name: str) -> list[str]:
        split_names = image_names.split(";")

        for name in split_names:
            self.blob_storage.save_image(product_name, name, self.zip_file.read(name))

        return split_names

    def create_product_from_row(self, row: list) -> Product:
        return Product(
            name=row[self.field_mapping["name"]],
            category=self.parse_categories(row[self.field_mapping["categories"]]),
            price=float(row[self.field_mapping["price"]]),
            description=row[self.field_mapping["description"]],
            image_paths=self.parse_images(row[self.field_mapping["image_names"]], row[self.field_mapping["name"]]),
            producer=row[self.field_mapping["producer"]],
            characteristics={},  # do later
            quantity=int(row[self.field_mapping["quantity"]])
        )






