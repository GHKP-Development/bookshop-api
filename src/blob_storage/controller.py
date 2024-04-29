from pathlib import Path
from PIL import Image


class BlobStorage:
    def __init__(self, base_directory: Path):
        self.base_directory = base_directory
        self.base_directory.mkdir(parents=True, exist_ok=True)
        self.images_directory = self.base_directory / 'images'
        self.images_directory.mkdir(parents=True, exist_ok=True)

    def save_image(self, product_name: str, image_name: str, image_data: bytes):
        target = self.images_directory / self._normalize_path_part(product_name) / self._normalize_path_part(image_name)
        target.parent.mkdir(parents=True, exist_ok=True)

        with target.open('wb+'):
            target.write_bytes(image_data)

    @staticmethod
    def _normalize_path_part(part: str) -> str:
        for char in "/\\ ,":
            part = part.replace(char, "_")

        return part

    def find_all_images_for_product(self, product_name: str) -> list[Image]:
        product_images_dir = Path(self.images_directory / self._normalize_path_part(product_name))
        if not product_images_dir.exists():
            return []

        if product_images_dir.is_file():
            raise RuntimeError(f"Path {product_images_dir} is file not directory")

        image_paths = []
        for image in product_images_dir.glob('*'):
            image_paths.append(Image.open(image))

        return image_paths
