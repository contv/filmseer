from fastapi import APIRouter, Request
from pydantic import BaseModel
from tortoise.exceptions import OperationalError
from tortoise.transactions import in_transaction
from datetime import datetime

from app.models.db.helpful_votes import HelpfulVotes
from app.models.db.funny_votes import FunnyVotes
from app.models.db.spoiler_votes import SpoilerVotes
from app.models.db.reviews import Reviews

from app.utils.wrapper import ApiException, Wrapper, wrap

router = APIRouter()
override_prefix = None
override_prefix_all = None


class NumVote(BaseModel):
    count: int


@router.post("/{id}/helpful", response_model=Wrapper[NumVote])
async def mark_review_helpful(id: str, request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2600, "You must be logged in to mark the review as helpful."
        )
    try:
        async with in_transaction():
            await HelpfulVotes.get_or_create(review_id=id, user_id=user_id)
            await HelpfulVotes.filter(review_id=id, user_id=user_id).update(
                delete_date=None
            )
        num_helpful = await HelpfulVotes.filter(review_id=id, delete_date=None).count()
        await Reviews.filter(review_id=id).update(num_helpful=num_helpful)
    except OperationalError:
        return ApiException(500, 2501, "An exception occurred")
    return wrap({"count": num_helpful})


@router.post("/{id}/funny", response_model=Wrapper[NumVote])
async def mark_review_funny(request: Request, id: str) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2601, "You must be logged in to mark the review as funny."
        )
    try:
        async with in_transaction():
            await FunnyVotes.get_or_create(review_id=id, user_id=user_id)
            await FunnyVotes.filter(review_id=id, user_id=user_id).update(
                delete_date=None
            )
        num_funny = await FunnyVotes.filter(review_id=id, delete_date=None).count()
        await Reviews.filter(review_id=id).update(num_funny=num_funny)
    except OperationalError:
        return ApiException(500, 2501, "An exception occurred")
    return wrap({"count": num_funny})


@router.post("/{id}/spoiler", response_model=Wrapper[NumVote])
async def mark_review_spoiler(request: Request, id: str) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2602, "You must be logged in to mark the review as spoiler."
        )
    try:
        async with in_transaction():
            await SpoilerVotes.get_or_create(review_id=id, user_id=user_id)
            await SpoilerVotes.filter(review_id=id, user_id=user_id).update(
                delete_date=None
            )
        num_spoiler = await SpoilerVotes.filter(review_id=id, delete_date=None).count()
        await Reviews.filter(review_id=id).update(num_spoiler=num_spoiler)
    except OperationalError:
        return ApiException(500, 2501, "An exception occurred")
    return wrap({"count": num_spoiler})


@router.delete("/{id}/helpful", response_model=Wrapper[NumVote])
async def unmark_review_helpful(request: Request, id: str) -> Wrapper[dict]:
    user_id = "058ffe8f-d27c-5e6a-21aa-c41401b996f9"
    if not user_id:
        return ApiException(
            401, 2603, "You must be logged in to unmark the review as helpful."
        )
    try:
        async with in_transaction():
            await HelpfulVotes.get_or_create(review_id=id, user_id=user_id)
            await HelpfulVotes.filter(review_id=id, user_id=user_id).update(
                delete_date=datetime.now()
            )
        num_helpful = await HelpfulVotes.filter(review_id=id, delete_date=None).count()
        await Reviews.filter(review_id=id).update(num_helpful=num_helpful)
    except OperationalError:
        return ApiException(500, 2501, "An exception occurred")
    return wrap({"count": num_helpful})


@router.delete("/{id}/funny", response_model=Wrapper[NumVote])
async def unmark_review_funny(request: Request, id: str) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2604, "You must be logged in to unmark the review as funny."
        )
    try:
        async with in_transaction():
            await FunnyVotes.filter(review_id=id, user_id=user_id).delete()
            await FunnyVotes.filter(review_id=id, user_id=user_id).update(
                delete_date=datetime.now()
            )
        num_funny = await FunnyVotes.filter(review_id=id, delete_date=None).count()
        await Reviews.filter(review_id=id).update(num_funny=num_funny)
    except OperationalError:
        return ApiException(500, 2501, "An exception occurred")
    return wrap({"count": num_funny})


@router.delete("/{id}/spoiler", response_model=Wrapper[NumVote])
async def unmark_review_spoiler(request: Request, id: str) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2605, "You must be logged in to unmark the review as spoiler."
        )
    try:
        async with in_transaction():
            await SpoilerVotes.filter(review_id=id, user_id=user_id).delete()
            await SpoilerVotes.filter(review_id=id, user_id=user_id).update(
                delete_date=datetime.now()
            )
        num_spoiler = await SpoilerVotes.filter(review_id=id, delete_date=None).count()
        await Reviews.filter(review_id=id).update(num_spoiler=num_spoiler)
    except OperationalError:
        return ApiException(500, 2501, "An exception occurred")
    return wrap({"count": num_spoiler})
