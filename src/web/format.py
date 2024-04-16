from flask import jsonify, Response


def json_error(status_code: int, error: str) -> Response:
    resp = jsonify({"error": error})
    resp.status_code = status_code

    return resp
