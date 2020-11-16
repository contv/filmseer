from typing import Any

from fastapi import APIRouter

router = APIRouter()
override_prefix = ''
override_prefix_all = None

# a test route used as a sanity check
@router.get("/", tags=["index"])
def api_index() -> Any:
    return "hello world! This is the index of the API."