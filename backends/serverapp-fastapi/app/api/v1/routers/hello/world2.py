from typing import Any

from fastapi import APIRouter, Request

router = APIRouter()
override_prefix = None
override_prefix_all = None


@router.get("/hello2")
def api_index(request: Request) -> Any:
    return "hello world2! This is a demo of directory routing."
