from typing import Any
from fastapi import APIRouter

router = APIRouter()
override_prefix = None
override_prefix_all = None


@router.get("/", tags=["helloworld"])
def api_index() -> Any:
    return "hello world! This is a demo of directory routing."
