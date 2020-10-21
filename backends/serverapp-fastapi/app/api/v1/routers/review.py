from fastapi import APIRouter, Request

from app.models.db.helpful_votes import HelpfulVotes
from app.models.db.funny_votes import FunnyVotes
from app.models.db.reviews import Reviews

from app.utils.wrapper import ApiException, Wrapper, wrap

router = APIRouter()
override_prefix = None
override_prefix_all = None


@router.post("/review/{id}/helpful")
async def mark_review_helpful(request: Request, id: str) -> Wrapper[dict]:
    return wrap({})


@router.post("/review/{id}/funny")
async def mark_review_funny(request: Request, id: str) -> Wrapper[dict]:
    return wrap({})


@router.post("/review/{id}/spoiler")
async def mark_review_spoiler(request: Request, id: str) -> Wrapper[dict]:
    return wrap({})


@router.delete("/review/{id}/helpful")
async def unmark_review_helpful(request: Request, id: str) -> Wrapper[dict]:
    return wrap({})


@router.delete("/review/{id}/funny")
async def unmark_review_funny(request: Request, id: str) -> Wrapper[dict]:
    return wrap({})


@router.delete("/review/{id}/spoiler")
async def unmark_review_spoiler(request: Request, id: str) -> Wrapper[dict]:
    return wrap({})
