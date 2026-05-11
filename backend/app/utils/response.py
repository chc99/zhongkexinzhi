from typing import Any


def success(data: Any = None, message: str = "success") -> dict:
    return {"code": 200, "message": message, "data": data}


def error(code: int = 500, message: str = "error", data: Any = None) -> dict:
    return {"code": code, "message": message, "data": data}


def page_result(items: list, total: int, page: int, page_size: int) -> dict:
    return success({"list": items, "total": total, "page": page, "page_size": page_size})
