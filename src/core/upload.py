import csv
import zipfile

from src.core.category import ProductCategory
from src.core.product import Product


class UploadParser:
    def __init__(self, zip_file: zipfile.ZipFile):
        self.zip_file: zipfile.ZipFile = zip_file
        self.products_to_create: list[Product] = []
        self.products_to_update: list[Product] = []
        self.products_to_delete: list[Product] = []
        self.field_mapping: dict[str, int] = {}

    def parse(self):
        with self.zip_file.open("manifest.csv") as csv_file:
            reader = csv.reader(csv_file)
            header = next(reader)
            self.map_csv_headers(header)
            for row in reader:
                match row[self.field_mapping["action"]]:
                    case "C":
                        product = Product(
                            name=row[self.field_mapping["name"]],
                            category=self.parse_categories(row[self.field_mapping["categories"]]),
                            price=float(row[self.field_mapping["price"]]),
                            description=row[self.field_mapping["description"]],
                            image_path=self.parse_images(row[self.field_mapping["image_names"]]),
                            producer=row[self.field_mapping["producer"]],
                            characteristics=None, #do later
                            quantity=int(row[self.field_mapping["quantity"]])
                        )
                        self.products_to_create.append(product)
                    case "U":

                    case "D":

    def parse_categories(self, categories: str):
        split_categories = categories.split(";")

        sum_ = 0
        for category in split_categories:
            sum_ += ProductCategory.lookup(category)

        return sum_

    def map_csv_headers(self, header: list[str]):
        for index, column in enumerate(header):
            self.field_mapping[column.casefold()] = index

    def parse_images(self, image_names: str):
        split_names = image_names.split(";")

        for name in split_names:
            with open(name, "wb+") as destination:
                destination.write(self.zip_file.read(name))




