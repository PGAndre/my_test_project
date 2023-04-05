from typing import Any

from fastapi import HTTPException


class ClientErrorAPIException(HTTPException):
    """Исключение для HTTP code: (400..499]"""

    def __init__(self, status_code: int, body_json: Any):
        self.status_code = status_code
        self.detail = body_json


class BadRequestAPIException(ClientErrorAPIException):
    """Исключение для HTTP code: 400"""


class ServerErrorAPIException(HTTPException):
    """Исключение для HTTP code: [500..)"""

    def __init__(self, status_code: int, body: str):
        self.status_code = status_code
        self.detail = body
