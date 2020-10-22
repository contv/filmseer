from fastapi import APIRouter, Request
from tortoise.exceptions import OperationalError
from tortoise.transactions import in_transaction

from app.models.db.helpful_votes import HelpfulVotes
from app.models.db.funny_votes import FunnyVotes
from app.models.db.spoiler_votes import SpoilerVotes
from app.models.db.reviews import Reviews

from app.utils.wrapper import ApiException, Wrapper, wrap

router = APIRouter()
override_prefix = None
override_prefix_all = None


@router.post("/{id}/helpful")
async def mark_review_helpful(request: Request, id: str) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2500, "You must be logged in to mark the review as helpful."
        )
    try:
        async with in_transaction():
            await HelpfulVotes.get_or_create(review_id=id, user_id=user_id)
        num_helpful = await HelpfulVotes.filter(review_id=id).count()
        await Reviews.filter(review_id=id).update(helpful_count=num_helpful)
    except OperationalError:
        return ApiException(401, 2501, "An exception occurred")
    return wrap(num_helpful)


@router.post("/{id}/funny")
async def mark_review_funny(request: Request, id: str) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2500, "You must be logged in to mark the review as funny."
        )
    try:
        async with in_transaction():
            await FunnyVotes.get_or_create(review_id=id, user_id=user_id)
        num_funny = await FunnyVotes.filter(review_id=id).count()
        await Reviews.filter(review_id=id).update(funny_count=num_funny)
    except OperationalError:
        return ApiException(401, 2501, "An exception occurred")
    return wrap(num_funny)


@router.post("/{id}/spoiler")
async def mark_review_spoiler(request: Request, id: str) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2500, "You must be logged in to mark the review as spoiler."
        )
    try:
        async with in_transaction():
            await SpoilerVotes.get_or_create(review_id=id, user_id=user_id)
        num_spoiler = await SpoilerVotes.filter(review_id=id).count()
        await Reviews.filter(review_id=id).update(spoiler_count=num_spoiler)
    except OperationalError:
        return ApiException(401, 2501, "An exception occurred")
    return wrap(num_spoiler)


@router.delete("/{id}/helpful")
async def unmark_review_helpful(request: Request, id: str) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2500, "You must be logged in to unmark the review as helpful."
        )
    try:
        async with in_transaction():
            await HelpfulVotes.filter(review_id=id, user_id=user_id).delete()
        num_helpful = await HelpfulVotes.filter(review_id=id).count()
        await Reviews.filter(review_id=id).update(helpful_count=num_helpful)
    except OperationalError:
        return ApiException(401, 2501, "An exception occurred")
    return wrap(num_helpful)


@router.delete("/{id}/funny")
async def unmark_review_funny(request: Request, id: str) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2500, "You must be logged in to unmark the review as funny."
        )
    try:
        async with in_transaction():
            await FunnyVotes.filter(review_id=id, user_id=user_id).delete()
        num_funny = await FunnyVotes.filter(review_id=id).count()    
        await Reviews.filter(review_id=id).update(funny_count=num_funny)
    except OperationalError:
        return ApiException(401, 2501, "An exception occurred")
    return wrap(num_funny)


@router.delete("/{id}/spoiler")
async def unmark_review_spoiler(request: Request, id: str) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2500, "You must be logged in to unmark the review as spoiler."
        )
    try:
        async with in_transaction():
            await SpoilerVotes.filter(review_id=id, user_id=user_id).delete()
        num_spoiler = await SpoilerVotes.filter(review_id=id).count()    
        await Reviews.filter(review_id=id).update(spoiler_count=num_spoiler)
    except OperationalError:
        return ApiException(401, 2501, "An exception occurred")
    return wrap(num_spoiler)
