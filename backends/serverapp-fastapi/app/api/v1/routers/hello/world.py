from typing import Any

from fastapi import APIRouter, Request

router = APIRouter()
override_prefix = None
override_prefix_all = None


@router.get("/", tags=["helloworld"])
def api_index(request: Request) -> Any:
    request.session["foo"] = "bar"
    return "hello world! This is a demo of directory routing."
