import http
from datetime import datetime

from flask import Flask, Response, jsonify, request

from src.context import ThreadLocalContextTable
from src.core.product import Product
from src.db.connection import Database
from src.utils.logging.logger import Logger
from src.web.format import json_error


class Application:
    def __init__(self, port: int, database: Database, logger: Logger):
        self._app: Flask = Flask("bookshop")
        self._port: int = port
        self._db: Database = database
        self._logger: Logger = logger
        self._start_time: datetime = datetime.now()

        self._app.add_url_rule('/products/<int:product_id>', 'product', self._handle_product, methods=['GET', 'DELETE'])
        self._app.add_url_rule('/products/search', 'search_products', self.search_products, methods=['GET'])
        self._app.add_url_rule('/health', 'health_check', self._health, methods=['GET'])

    def run(self, port: int = 0):
        """
        Run the application. If no port is specified, the port from the constructor is used. If no port is specified
        in the constructor, port 80 is used.
        If debug is True, the application is run in debug mode (raw flask). Otherwise, the application is run in
        production mode (waitress WSGI server)
        """
        if not port:
            if not self._port:
                port = 80
            else:
                port = self._port

        self._logger.info(f"Running in debug mode (raw flask) on {port=}")
        return self._app.run(host="0.0.0.0", port=port, debug=False)

    @staticmethod
    def _instrument_thread():
        with ThreadLocalContextTable() as ctx:
            if request_id := request.headers.get("X-Request-Id"):
                ctx.upsert(key="request_id", value=request_id)

            source = request.remote_addr
            if ff := request.headers.get("X-Forwarded-For"):
                source = ff
            ctx.upsert(key="source", value=source)

    def get_product(self, product_id: int = None) -> Response:
        self._logger.debug(f"Product id is: {product_id}")
        db_product = self._db.get_product(product_id)
        return jsonify(db_product)

    def search_products(self) -> Response:
        self._instrument_thread()
        kwargs = {}
        if name := request.args.get("name"):
            kwargs["name"] = name
        if category := request.args.get("category"):
            kwargs["category"] = category
        if min_price := request.args.get("min_price"):
            kwargs["min_price"] = min_price
        if max_price := request.args.get("max_price"):
            kwargs["max_price"] = max_price
        if producer := request.args.get("producer"):
            kwargs["producer"] = producer

        try:
            return jsonify(self._db.search_products(**kwargs))
        except Exception as exc:
            self._logger.error(f"Search products failed: {exc}")
            return json_error(http.HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))

    def delete_product(self, product_id: int) -> bool:
        return self._db.delete_product(product_id)

    def _handle_product(self, product_id: int):
        self._instrument_thread()
        match request.method:
            case 'GET':
                return self.get_product(product_id)
            case 'DELETE':
                return self.delete_product(product_id)

    def update_product(self):
        self._instrument_thread()
        product = Product.from_dict(request.get_json())
        if not product.id:
            return json_error(status_code=http.HTTPStatus.BAD_REQUEST, error="No product_id provided in request body")
        return "", self._db.update_product(product=product)

    def _health(self) -> Response:
        time_delta = datetime.now() - self._start_time
        payload = {
            "uptime": str(time_delta)
        }
        return jsonify(payload)

    def _configure(self):
        self._app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True